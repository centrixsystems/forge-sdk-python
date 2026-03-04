use dagger_sdk::{Directory, Query};
use eyre::WrapErr;

use crate::containers::python_builder;

/// Run ruff linter on the SDK source.
pub async fn run(client: &Query, source: Directory) -> eyre::Result<String> {
    let output = python_builder(client, source)
        .with_exec(vec!["pip", "install", "ruff"])
        .with_exec(vec!["ruff", "check", "forge_sdk/"])
        .with_exec(vec!["sh", "-c", "echo 'check: ruff passed'"])
        .stdout()
        .await
        .wrap_err("check failed")?;

    Ok(output)
}
