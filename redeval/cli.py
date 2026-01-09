"""
Unified CLI interface for RedEval.
Provides a single entry point for all evaluation operations.
"""

import argparse
import sys
import logging
from typing import List, Optional
from pathlib import Path

from redeval.pipeline import PipelineOrchestrator, PipelineConfig, PipelinePhase
from redeval.config import env_config


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        description="RedEval: LLM Safety Evaluation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline
  python -m redeval.cli run-pipeline --models "Qwen/Qwen2.5-7B-Instruct" "gpt-4o-mini"
  
  # Run specific phases
  python -m redeval.cli run-pipeline --phases generate_attack run_attack eval_attack
  
  # Run individual components
  python -m redeval.cli generate-attack --config ./recipes/attack/base-close.yml
  python -m redeval.cli run-attack --config ./recipes/attack/base-open.yml --model "Qwen/Qwen2.5-7B-Instruct"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser("run-pipeline", help="Run complete evaluation pipeline")
    pipeline_parser.add_argument(
        "--models", 
        nargs="+", 
        default=None,  # Will be computed from open + closed source models
        help="Models to evaluate (overrides open/closed source model lists)"
    )
    pipeline_parser.add_argument(
        "--open-source-models",
        nargs="+",
        default=None,  # Will use env_config values
        help="Open source models to evaluate (default: from REDEVAL_OPEN_SOURCE_MODELS env var)"
    )
    pipeline_parser.add_argument(
        "--closed-source-models",
        nargs="+",
        default=None,  # Will use env_config values
        help="Closed source models to evaluate (default: from REDEVAL_CLOSED_SOURCE_MODELS env var)"
    )
    pipeline_parser.add_argument(
        "--phases",
        nargs="+",
        choices=[phase.value for phase in PipelinePhase],
        help="Specific phases to run (default: all phases)"
    )
    pipeline_parser.add_argument(
        "--num-samples",
        type=int,
        default=None,  # Will use env_config.num_samples
        help="Number of samples to process (default: from REDEVAL_NUM_SAMPLES env var, -1 for all)"
    )
    pipeline_parser.add_argument(
        "--seed",
        type=int,
        default=None,  # Will use env_config.seed
        help="Random seed (default: from REDEVAL_SEED env var)"
    )
    
    # Individual component commands
    _add_generate_attack_parser(subparsers)
    _add_run_attack_parser(subparsers)
    _add_eval_attack_parser(subparsers)
    _add_run_refuse_parser(subparsers)
    _add_eval_refuse_parser(subparsers)
    _add_score_parser(subparsers)
    
    return parser


def _add_generate_attack_parser(subparsers):
    """Add generate-attack subcommand."""
    parser = subparsers.add_parser("generate-attack", help="Generate attack prompts")
    parser.add_argument("--config", type=str, required=True, help="Configuration file path")
    parser.add_argument("--num-samples", type=int, default=10, help="Number of samples")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument("--split", type=str, default="train", help="Dataset split")
    parser.add_argument("--field", type=str, default="prompt", help="Field to extract")


def _add_run_attack_parser(subparsers):
    """Add run-attack subcommand."""
    parser = subparsers.add_parser("run-attack", help="Run attack evaluation")
    parser.add_argument("--config", type=str, required=True, help="Configuration file path")
    parser.add_argument("--model", type=str, help="Model name to evaluate")


def _add_eval_attack_parser(subparsers):
    """Add eval-attack subcommand."""
    parser = subparsers.add_parser("eval-attack", help="Evaluate attack results")
    parser.add_argument("--config", type=str, required=True, help="Configuration file path")
    parser.add_argument("--log-dir", type=str, required=True, help="Log directory")


def _add_run_refuse_parser(subparsers):
    """Add run-refuse subcommand."""
    parser = subparsers.add_parser("run-refuse", help="Run refuse evaluation")
    parser.add_argument("--config", type=str, required=True, help="Configuration file path")
    parser.add_argument("--model", type=str, help="Model name to evaluate")
    parser.add_argument("--num-samples", type=int, default=10, help="Number of samples")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument("--split", type=str, default="train", help="Dataset split")
    parser.add_argument("--field", type=str, default="prompt", help="Field to extract")


def _add_eval_refuse_parser(subparsers):
    """Add eval-refuse subcommand."""
    parser = subparsers.add_parser("eval-refuse", help="Evaluate refuse results")
    parser.add_argument("--config", type=str, required=True, help="Configuration file path")
    parser.add_argument("--log-dir", type=str, required=True, help="Log directory")


def _add_score_parser(subparsers):
    """Add score subcommand."""
    parser = subparsers.add_parser("score", help="Calculate scores")
    parser.add_argument("--log-dir", type=str, required=True, help="Log directory")
    parser.add_argument("--keyword", type=str, default="unsafe", help="Keyword to score")


def run_pipeline_command(args) -> int:
    """Execute the pipeline command."""
    logger = logging.getLogger(__name__)
    
    # Convert phase strings to enum values
    phases = None
    if args.phases:
        phases = [PipelinePhase(phase) for phase in args.phases]
    
    # Use env_config defaults if CLI args are not provided
    open_source_models = args.open_source_models if args.open_source_models is not None else env_config.open_source_models
    closed_source_models = args.closed_source_models if args.closed_source_models is not None else env_config.closed_source_models
    num_samples = args.num_samples if args.num_samples is not None else env_config.num_samples
    seed = args.seed if args.seed is not None else env_config.seed
    
    # If models is provided, use it; otherwise combine open + closed source models
    if args.models is not None:
        models = args.models
    else:
        models = open_source_models + closed_source_models
    
    logger.info(f"Open source models: {open_source_models}")
    logger.info(f"Closed source models: {closed_source_models}")
    logger.info(f"All models: {models}")
    
    # Create pipeline configuration
    config = PipelineConfig(
        models=models,
        open_source_models=open_source_models,
        closed_source_models=closed_source_models,
        phases=phases,
        num_samples=num_samples,
        seed=seed
    )
    
    # Run pipeline
    orchestrator = PipelineOrchestrator(config)
    
    try:
        results = orchestrator.run_complete_pipeline()
        logger.info("Pipeline completed successfully")
        logger.info(f"Results: {results}")
        return 0
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        return 1


def run_individual_command(args) -> int:
    """Execute individual component commands."""
    logger = logging.getLogger(__name__)
    
    try:
        if args.command == "generate-attack":
            from redeval.generate_attack import run
            from redeval.configs.attack import AttackRunner
            
            config = AttackRunner.load(args.config)
            run(config, args.num_samples, False, args.seed, args.split, args.field)
            
        elif args.command == "run-attack":
            from redeval.run_attack import run
            from redeval.configs.attack import AttackRunner
            
            config = AttackRunner.load(args.config)
            if args.model:
                config.target_llm.model_kwargs["model"] = args.model
            run(config)
            
        elif args.command == "eval-attack":
            from redeval.eval_attack import run
            import argparse as ap
            
            eval_args = ap.Namespace(config_path=args.config, log_dir=args.log_dir)
            run(eval_args)
            
        elif args.command == "run-refuse":
            from redeval.run_refuse import run
            from redeval.configs.refuse import RefuseRunner
            
            config = RefuseRunner.load(args.config)
            if args.model:
                config.target_llm.model_kwargs["model"] = args.model
            run(config, args.num_samples, False, args.seed, args.split, args.field)
            
        elif args.command == "eval-refuse":
            from redeval.eval_refuse import run
            import argparse as ap
            
            eval_args = ap.Namespace(config_path=args.config, log_dir=args.log_dir)
            run(eval_args)
            
        elif args.command == "score":
            from redeval.score import main
            import argparse as ap
            
            score_args = ap.Namespace(log_dir=args.log_dir, keyword=args.keyword)
            main(score_args)
            
        logger.info(f"Command '{args.command}' completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Command '{args.command}' failed: {str(e)}")
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    env_config.setup_logging()
    logger = logging.getLogger(__name__)
    
    # Validate environment
    if not env_config.validate():
        logger.error("Environment validation failed. Please check your configuration.")
        logger.error("Required environment variables: OPENAI_API_KEY, HUGGINGFACE_TOKEN")
        return 1
    
    # Route to appropriate handler
    if args.command == "run-pipeline":
        return run_pipeline_command(args)
    else:
        return run_individual_command(args)


if __name__ == "__main__":
    main()
