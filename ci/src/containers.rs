use dagger_sdk::{Container, Directory, Query};

/// Base Python container with pip cache.
pub fn python_builder(client: &Query, source: Directory) -> Container {
    let pip_cache = client.cache_volume("forge-sdk-python-pip");

    client
        .container()
        .from("python:3.12-slim")
        .with_mounted_directory("/build", source)
        .with_workdir("/build")
        .with_mounted_cache("/root/.cache/pip", pip_cache)
}
