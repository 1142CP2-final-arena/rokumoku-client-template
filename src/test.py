#!/usr/bin/env python3
"""Runtime smoke tests for the Rokumoku bot sandbox."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def log(message: str) -> None:
    print(f"[runtime-test] {message}", flush=True)


def run_command(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        command = " ".join(args)
        raise RuntimeError(
            f"command failed: {command}\n"
            f"stdout:\n{exc.stdout}\n"
            f"stderr:\n{exc.stderr}"
        ) from exc


def test_tmp_writable() -> None:
    tmp_root = Path("/tmp")
    if not tmp_root.is_dir():
        raise RuntimeError("/tmp does not exist")
    with tempfile.TemporaryDirectory(prefix="rokumoku-test-", dir=tmp_root) as tmp_dir:
        marker = Path(tmp_dir) / "write-test.txt"
        marker.write_text("ok\n", encoding="utf-8")
        if marker.read_text(encoding="utf-8") != "ok\n":
            raise RuntimeError("failed to read back /tmp write test")
    log("/tmp writable")


def test_python_packages() -> None:
    import gymnasium
    import requests
    import scipy
    import sseclient
    import tqdm

    log(
        "imports ok: "
        f"requests={requests.__version__}, "
        f"sseclient={getattr(sseclient, '__version__', 'unknown')}, "
        f"scipy={scipy.__version__}, "
        f"gymnasium={gymnasium.__version__}, "
        f"tqdm={tqdm.__version__}"
    )


def test_numpy_scipy() -> None:
    import numpy as np
    from scipy.signal import convolve2d

    board = np.arange(225, dtype=np.float32).reshape(15, 15)
    kernel = np.ones((3, 3), dtype=np.float32)
    result = convolve2d(board, kernel, mode="valid")
    if result.shape != (13, 13):
        raise RuntimeError(f"unexpected scipy convolve shape: {result.shape}")
    log("numpy/scipy numeric ops ok")


def test_numba() -> None:
    os.environ.setdefault("NUMBA_CACHE_DIR", "/tmp/numba_cache")
    Path(os.environ["NUMBA_CACHE_DIR"]).mkdir(parents=True, exist_ok=True)

    import numpy as np
    from numba import njit

    @njit(cache=True)
    def weighted_sum(values):
        total = 0.0
        for index in range(values.size):
            total += values[index] * (index + 1)
        return total

    values = np.arange(10, dtype=np.float64)
    result = weighted_sum(values)
    if abs(result - 330.0) > 1e-9:
        raise RuntimeError(f"unexpected numba result: {result}")
    log(f"numba JIT/cache ok: {os.environ['NUMBA_CACHE_DIR']}")


def test_torch_cpu() -> None:
    import torch
    from torch import nn
    from torch.nn import functional as F

    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(225, 32), nn.ReLU(), nn.Linear(32, 225))
    model.eval()
    sample = torch.zeros((1, 225), dtype=torch.float32)
    with torch.no_grad():
        probs = F.softmax(torch.sigmoid(model(sample)), dim=-1)
    if probs.shape != (1, 225):
        raise RuntimeError(f"unexpected torch output shape: {tuple(probs.shape)}")
    if not torch.isfinite(probs).all():
        raise RuntimeError("torch output contains non-finite values")
    log(f"torch CPU inference ok: torch={torch.__version__}")


def test_cpp_toolchain() -> None:
    with tempfile.TemporaryDirectory(prefix="rokumoku-cpp-", dir="/tmp") as tmp_dir:
        tmp_path = Path(tmp_dir)
        source = tmp_path / "engine.cpp"
        makefile = tmp_path / "Makefile"
        source.write_text(
            "\n".join(
                [
                    "#include <iostream>",
                    "int main() {",
                    "    std::cout << 42 << std::endl;",
                    "    return 0;",
                    "}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        makefile.write_text(
            "\n".join(
                [
                    "CXX ?= g++",
                    "CXXFLAGS ?= -O2 -std=c++20",
                    "engine: engine.cpp",
                    "\t$(CXX) $(CXXFLAGS) engine.cpp -o engine",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        run_command(["make", "-C", str(tmp_path), "engine"])
        result = run_command([str(tmp_path / "engine")])
        if result.stdout.strip() != "42":
            raise RuntimeError(f"unexpected C++ executable output: {result.stdout!r}")
    log("g++/make C++ build ok")


def main() -> int:
    log(f"python={sys.version.split()[0]}")
    checks = [
        test_tmp_writable,
        test_python_packages,
        test_numpy_scipy,
        test_numba,
        test_torch_cpu,
        test_cpp_toolchain,
    ]
    for check in checks:
        check()
    log("all runtime checks passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        log(f"FAILED: {exc}")
        raise
