# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import json
from pathlib import Path

import torch

from build.utils import allowable_dtype_names, allowable_params_table
from download import download_and_convert, is_model_downloaded

default_device = "cpu"


# Handle CLI arguments that are common to a majority of subcommands.
def check_args(args, name: str) -> None:
    # Handle model download. Skip this for download, since it has slightly
    # different semantics.
    if (
        name not in ["download", "list", "remove"]
        and args.model
        and not is_model_downloaded(args.model, args.model_directory)
    ):
        download_and_convert(args.model, args.model_directory, args.hf_token)


def add_arguments_for_chat(parser):
    # Only chat specific options should be here
    _add_arguments_common(parser)


def add_arguments_for_browser(parser):
    # Only browser specific options should be here
    _add_arguments_common(parser)


def add_arguments_for_download(parser):
    # Only download specific options should be here
    _add_arguments_common(parser)


def add_arguments_for_generate(parser):
    # Only generate specific options should be here
    _add_arguments_common(parser)


def add_arguments_for_eval(parser):
    # Only eval specific options should be here
    _add_arguments_common(parser)


def add_arguments_for_export(parser):
    # Only export specific options should be here
    _add_arguments_common(parser)


def add_arguments_for_list(parser):
    # Only list specific options should be here
    _add_arguments_common(parser)


def add_arguments_for_remove(parser):
    # Only remove specific options should be here
    _add_arguments_common(parser)


def _add_arguments_common(parser):
    # Model specification. TODO Simplify this.
    # A model can be specified using a positional model name or HuggingFace
    # path. Alternatively, the model can be specified via --gguf-path or via
    # an explicit --checkpoint-dir, --checkpoint-path, or --tokenizer-path.
    parser.add_argument(
        "model",
        type=str,
        nargs="?",
        default=None,
        help="Model name for well-known models",
    )

    parser.add_argument(
        "--chat",
        action="store_true",
        help="Whether to start an interactive chat session",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Whether to use a web UI for an interactive chat session",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="Hello, my name is",
        help="Input prompt",
    )
    parser.add_argument(
        "--is-chat-model",
        action="store_true",
        help="Indicate that the model was trained to support chat functionality",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Initialize torch seed",
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=1,
        help="Number of samples",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=200,
        help="Maximum number of new tokens",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=200,
        help="Top-k for sampling",
    )
    parser.add_argument(
        "--temperature", type=float, default=0.8, help="Temperature for sampling"
    )
    parser.add_argument(
        "--compile",
        action="store_true",
        help="Whether to compile the model with torch.compile",
    )
    parser.add_argument(
        "--compile-prefill",
        action="store_true",
        help="Whether to compile the prefill. Improves prefill perf, but has higher compile times. (Requires `--parallel-prefill`)",
    )
    parser.add_argument(
        "--parallel-prefill",
        action="store_true",
        help="Whether to perform prefill in parallel, or one token at a time. Improves prefill perf. DSO and PTE models presently do not support parallel prefill.",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        default=None,
        help="Profile path.",
    )
    parser.add_argument(
        "--speculate-k",
        type=int,
        default=5,
        help="Speculative execution depth",
    )
    parser.add_argument(
        "--draft-checkpoint-path",
        type=Path,
        default=None,
        help="Use the specified draft checkpoint path",
    )
    parser.add_argument(
        "--checkpoint-path",
        type=Path,
        default="not_specified",
        help="Use the specified model checkpoint path",
    )
    parser.add_argument(
        "--params-path",
        type=Path,
        default=None,
        help="Use the specified parameter file",
    )
    parser.add_argument(
        "--gguf-path",
        type=Path,
        default=None,
        help="Use the specified GGUF model file",
    )
    parser.add_argument(
        "--tokenizer-path",
        type=Path,
        default=None,
        help="Use the specified model tokenizer file",
    )
    parser.add_argument(
        "--output-pte-path",
        type=str,
        default=None,
        help="Output to the specified ExecuTorch .pte model file",
    )
    parser.add_argument(
        "--output-dso-path",
        type=str,
        default=None,
        help="Output to the specified AOT Inductor .dso model file",
    )
    parser.add_argument(
        "--dso-path",
        type=Path,
        default=None,
        help="Use the specified AOT Inductor .dso model file",
    )
    parser.add_argument(
        "--pte-path",
        type=Path,
        default=None,
        help="Use the specified ExecuTorch .pte model file",
    )
    parser.add_argument(
        "-d",
        "--dtype",
        default="float32",
        choices=allowable_dtype_names(),
        help="Override the dtype of the model (default is the checkpoint dtype). Options: bf16, fp16, fp32",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--quantize",
        type=str,
        default="{ }",
        help=(
            'Quantization options. pass in as \'{"<mode>" : {"<argname1>" : <argval1>, "<argname2>" : <argval2>,...},}\' '
            + "modes are: embedding, linear:int8, linear:int4, linear:gptq, linear:hqq, linear:a8w4dq, precision."
        ),
    )
    parser.add_argument(
        "--draft-quantize",
        type=str,
        default="{ }",
        help=(
            "Quantization options. Same format as quantize, "
            + "or 'quantize' to indicate same options specified by "
            + "--quantize to main model. Applied to draft model."
        ),
    )
    parser.add_argument(
        "--params-table",
        type=str,
        default=None,
        choices=allowable_params_table(),
        help="Parameter table to use",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=default_device,
        choices=["cpu", "cuda", "mps"],
        help="Hardware device to use. Options: cpu, cuda, mps",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        type=str,
        default=["wikitext"],
        help="List of lm-eluther tasks to evaluate. Usage: --tasks task1 task2",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Number of samples to evaluate",
    )
    parser.add_argument(
        "--max-seq-length",
        type=int,
        default=None,
        help="Maximum length sequence to evaluate",
    )
    parser.add_argument(
        "--hf-token",
        type=str,
        default=None,
        help="A HuggingFace API token to use when downloading model artifacts",
    )
    parser.add_argument(
        "--model-directory",
        type=Path,
        default=".model-artifacts",
        help="The directory to store downloaded model artifacts",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port for the web server in browser mode",
    )


def arg_init(args):
    if hasattr(args, 'quantize') and Path(args.quantize).is_file():
        with open(args.quantize, "r") as f:
            args.quantize = json.loads(f.read())

    if hasattr(args, 'seed') and args.seed:
        torch.manual_seed(args.seed)
    return args
