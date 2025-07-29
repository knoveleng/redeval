"""
Centralized pipeline orchestrator for RedEval.
Manages the complete evaluation workflow including attack and refuse phases.
"""

import logging
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from redeval.config import env_config
from redeval.configs.attack import AttackRunner
from redeval.configs.refuse import RefuseRunner
from redeval.configs.eval import EvalRunner


class PipelinePhase(Enum):
    """Pipeline execution phases."""
    GENERATE_ATTACK = "generate_attack"
    RUN_ATTACK = "run_attack"
    EVAL_ATTACK = "eval_attack"
    RUN_REFUSE = "run_refuse"
    EVAL_REFUSE = "eval_refuse"
    SCORE = "score"


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution."""
    
    # Model configurations
    models: List[str]
    open_source_models: List[str]
    closed_source_models: List[str]
    
    # Dataset configurations
    attack_datasets: List[str] = None
    refuse_datasets: List[str] = None
    
    # Execution parameters
    num_samples: int = -1
    seed: int = 0
    split: str = "train"
    
    # Configuration paths
    attack_config_open: str = "./recipes/attack/base-open.yml"
    attack_config_close: str = "./recipes/attack/base-close.yml"
    refuse_config_open: str = "./recipes/refuse/base-open.yml"
    refuse_config_close: str = "./recipes/refuse/base-close.yml"
    eval_attack_config: str = "./recipes/attack/eval.yml"
    eval_refuse_config: str = "./recipes/refuse/eval.yml"
    
    # Phases to execute
    phases: List[PipelinePhase] = None
    
    def __post_init__(self):
        if self.phases is None:
            self.phases = list(PipelinePhase)
        
        if self.attack_datasets is None:
            self.attack_datasets = ["HarmBench"]
            
        if self.refuse_datasets is None:
            self.refuse_datasets = ["CoCoNot", "SGXSTest", "XSTest", "ORBench"]


class PipelineOrchestrator:
    """Orchestrates the complete RedEval pipeline."""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Setup environment
        env_config.setup_logging()
        
        if not env_config.validate():
            self.logger.warning("Some environment variables are missing. Pipeline may fail.")
    
    def run_complete_pipeline(self) -> Dict[str, Any]:
        """Run the complete evaluation pipeline."""
        self.logger.info("Starting RedEval pipeline execution")
        start_time = time.time()
        
        results = {}
        
        try:
            for phase in self.config.phases:
                self.logger.info(f"Executing phase: {phase.value}")
                phase_start = time.time()
                
                if phase == PipelinePhase.GENERATE_ATTACK:
                    results[phase.value] = self._run_generate_attack()
                elif phase == PipelinePhase.RUN_ATTACK:
                    results[phase.value] = self._run_attack()
                elif phase == PipelinePhase.EVAL_ATTACK:
                    results[phase.value] = self._eval_attack()
                elif phase == PipelinePhase.RUN_REFUSE:
                    results[phase.value] = self._run_refuse()
                elif phase == PipelinePhase.EVAL_REFUSE:
                    results[phase.value] = self._eval_refuse()
                elif phase == PipelinePhase.SCORE:
                    results[phase.value] = self._calculate_scores()
                
                phase_time = time.time() - phase_start
                self.logger.info(f"Phase {phase.value} completed in {phase_time:.2f}s")
                
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise
        
        total_time = time.time() - start_time
        self.logger.info(f"Pipeline completed in {total_time:.2f}s")
        
        return results
    
    def _run_generate_attack(self) -> Dict[str, Any]:
        """Execute attack generation phase."""
        from redeval.generate_attack import run
        
        config = AttackRunner.load(self.config.attack_config_close)
        
        run(
            config=config,
            num_samples=self.config.num_samples,
            shuffle=False,
            seed=self.config.seed,
            split=self.config.split,
            field="prompt"
        )
        
        return {"status": "completed", "config": self.config.attack_config_close}
    
    def _run_attack(self) -> Dict[str, Any]:
        """Execute attack phase."""
        from redeval.run_attack import run
        
        results = []
        
        # Process open-source models
        config = AttackRunner.load(self.config.attack_config_open)
        for model_name in self.config.open_source_models:
            self.logger.info(f"Running attack on open-source model: {model_name}")
            config.target_llm.model_kwargs["model"] = model_name
            run(config)
            results.append({"model": model_name, "type": "open_source"})
        
        # Process closed-source models
        config = AttackRunner.load(self.config.attack_config_close)
        for model_name in self.config.closed_source_models:
            self.logger.info(f"Running attack on closed-source model: {model_name}")
            config.target_llm.model_kwargs["model"] = model_name
            run(config)
            results.append({"model": model_name, "type": "closed_source"})
        
        return {"status": "completed", "models_processed": results}
    
    def _eval_attack(self) -> Dict[str, Any]:
        """Execute attack evaluation phase."""
        from redeval.eval_attack import run
        import argparse
        
        results = []
        config = EvalRunner.load(self.config.eval_attack_config)
        
        base_log_dir = Path("./logs/attack")
        method_names = ["direct", "human_jailbreak", "zeroshot"]
        
        for subdataset in self.config.attack_datasets:
            for method_name in method_names:
                for model_name in self.config.models:
                    log_dir = base_log_dir / subdataset / method_name / model_name
                    
                    if log_dir.exists():
                        self.logger.info(f"Evaluating attack: {subdataset}/{method_name}/{model_name}")
                        
                        # Create args object for compatibility
                        args = argparse.Namespace(
                            config_path=self.config.eval_attack_config,
                            log_dir=str(log_dir)
                        )
                        
                        run(args)
                        results.append({
                            "subdataset": subdataset,
                            "method": method_name,
                            "model": model_name
                        })
        
        return {"status": "completed", "evaluations": results}
    
    def _run_refuse(self) -> Dict[str, Any]:
        """Execute refuse phase."""
        from redeval.run_refuse import run
        
        results = []
        
        # Process open-source models
        config = RefuseRunner.load(self.config.refuse_config_open)
        for model_name in self.config.open_source_models:
            self.logger.info(f"Running refuse test on open-source model: {model_name}")
            config.target_llm.model_kwargs["model"] = model_name
            run(
                config=config,
                num_samples=10,
                shuffle=False,
                seed=self.config.seed,
                split=self.config.split,
                field="prompt"
            )
            results.append({"model": model_name, "type": "open_source"})
        
        # Process closed-source models
        config = RefuseRunner.load(self.config.refuse_config_close)
        for model_name in self.config.closed_source_models:
            self.logger.info(f"Running refuse test on closed-source model: {model_name}")
            config.target_llm.model_kwargs["model"] = model_name
            run(
                config=config,
                num_samples=10,
                shuffle=False,
                seed=self.config.seed,
                split=self.config.split,
                field="prompt"
            )
            results.append({"model": model_name, "type": "closed_source"})
        
        return {"status": "completed", "models_processed": results}
    
    def _eval_refuse(self) -> Dict[str, Any]:
        """Execute refuse evaluation phase."""
        from redeval.eval_refuse import run
        import argparse
        
        results = []
        base_log_dir = Path("./logs/refuse")
        method_names = ["base"]
        
        for subdataset in self.config.refuse_datasets:
            for method_name in method_names:
                for model_name in self.config.models:
                    log_dir = base_log_dir / subdataset / method_name / model_name
                    
                    if log_dir.exists():
                        self.logger.info(f"Evaluating refuse: {subdataset}/{method_name}/{model_name}")
                        
                        # Create args object for compatibility
                        args = argparse.Namespace(
                            config_path=self.config.eval_refuse_config,
                            log_dir=str(log_dir)
                        )
                        
                        run(args)
                        results.append({
                            "subdataset": subdataset,
                            "method": method_name,
                            "model": model_name
                        })
        
        return {"status": "completed", "evaluations": results}
    
    def _calculate_scores(self) -> Dict[str, Any]:
        """Calculate final scores."""
        from redeval.score import main
        import argparse
        
        results = {"attack": [], "refuse": []}
        
        # Score attack results
        base_log_dir = Path("./logs/attack")
        method_names = ["direct", "human_jailbreak", "zeroshot"]
        
        for subdataset in self.config.attack_datasets:
            for method_name in method_names:
                for model_name in self.config.models:
                    log_dir = base_log_dir / subdataset / method_name / model_name
                    
                    if log_dir.exists():
                        self.logger.info(f"Scoring attack: {subdataset}/{method_name}/{model_name}")
                        
                        args = argparse.Namespace(
                            log_dir=str(log_dir),
                            keyword="unsafe"
                        )
                        
                        main(args)
                        results["attack"].append({
                            "subdataset": subdataset,
                            "method": method_name,
                            "model": model_name
                        })
        
        # Score refuse results
        base_log_dir = Path("./logs/refuse")
        method_names = ["base"]
        
        for subdataset in self.config.refuse_datasets:
            for method_name in method_names:
                for model_name in self.config.models:
                    log_dir = base_log_dir / subdataset / method_name / model_name
                    
                    if log_dir.exists():
                        self.logger.info(f"Scoring refuse: {subdataset}/{method_name}/{model_name}")
                        
                        args = argparse.Namespace(
                            log_dir=str(log_dir),
                            keyword="unpass"
                        )
                        
                        main(args)
                        results["refuse"].append({
                            "subdataset": subdataset,
                            "method": method_name,
                            "model": model_name
                        })
        
        return {"status": "completed", "scores": results}
