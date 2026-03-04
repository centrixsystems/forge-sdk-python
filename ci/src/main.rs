use clap::{Parser, Subcommand};
use dagger_sdk::Query;
use eyre::WrapErr;

mod containers;
mod stages;

#[derive(Parser)]
#[command(name = "forge-sdk-python-ci")]
struct Cli {
    #[command(subcommand)]
    command: Command,

    /// Path to SDK source directory
    #[arg(long, default_value = "..")]
    source: String,
}

#[derive(Subcommand)]
enum Command {
    /// Run lint checks (ruff)
    Check,
    /// Run pytest
    Test,
    /// Run all stages
    All,
}

#[tokio::main]
async fn main() -> eyre::Result<()> {
    color_eyre::install()?;
    let cli = Cli::parse();

    let client = dagger_sdk::connect().await?;

    let source = client
        .host()
        .directory_opts(
            &cli.source,
            dagger_sdk::HostDirectoryOptsBuilder::default()
                .exclude(vec!["__pycache__/", ".git/", "ci/", "*.egg-info/", "dist/", ".venv/"])
                .build()?,
        )
        .id()
        .await
        .wrap_err("failed to load source")?;

    let source = client.directory(source);

    match cli.command {
        Command::Check => {
            let out = stages::check::run(&client, source).await?;
            println!("{out}");
        }
        Command::Test => {
            let out = stages::test::run(&client, source).await?;
            println!("{out}");
        }
        Command::All => {
            let (check, test) = tokio::try_join!(
                stages::check::run(&client, source.clone()),
                stages::test::run(&client, source),
            )?;
            println!("{check}");
            println!("{test}");
        }
    }

    Ok(())
}
