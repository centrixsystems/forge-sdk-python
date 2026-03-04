use dagger_sdk::{Directory, Query};
use eyre::WrapErr;

use crate::containers::python_builder;

/// Install dev dependencies and run pytest.
pub async fn run(client: &Query, source: Directory) -> eyre::Result<String> {
    let output = python_builder(client, source)
        .with_exec(vec!["pip", "install", "-e", ".[dev]"])
        .with_exec(vec!["pytest", "tests/"])
        .with_exec(vec!["sh", "-c", "echo 'test: pytest passed'"])
        .stdout()
        .await
        .wrap_err("test failed")?;

    Ok(output)
}
