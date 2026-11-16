@echo off
set "PATH=C:\prepmate-core\bin;%USERPROFILE%\.cargo\bin;%PATH%"
set "CARGO_TARGET_DIR=C:\prepmate-core\target"
cargo build --release
