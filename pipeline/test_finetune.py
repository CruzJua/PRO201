"""
Tests for finetune.py, the script that continues training the ALREADY
TRAINED cnn_model.pt checkpoint rather than starting from scratch (see
config.py's committed-model design note for why a checkpoint is expected to
already exist here).

Only the pre-training-loop contract is tested: default hyperparameters
(lower LR than train.py's from-scratch default, since we're nudging
converged weights) and the fail-fast behavior when there's no checkpoint to
fine-tune. Actually running the training loop belongs to manual end-to-end
validation (per CLAUDE.md's "long-running jobs" rule), not a unit test.
"""

import pytest

import config
import finetune


def test_default_learning_rate_is_lower_than_train_pys_from_scratch_default():
    args = finetune.parse_args([])
    assert args.lr < config.LEARNING_RATE


def test_epochs_and_batch_size_defaults_are_sane():
    args = finetune.parse_args([])
    assert args.epochs > 0
    assert args.batch_size == config.BATCH_SIZE


def test_cli_overrides_are_respected():
    args = finetune.parse_args(["--epochs", "3", "--lr", "5e-5", "--batch-size", "16"])
    assert args.epochs == 3
    assert args.lr == 5e-5
    assert args.batch_size == 16


def test_main_fails_fast_when_no_checkpoint_exists_to_fine_tune(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "MODEL_PATH", tmp_path / "does_not_exist.pt")
    with pytest.raises(FileNotFoundError):
        finetune.main([])
