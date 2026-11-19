# NexaAI

NexaAI is an evolving AI engineering project that combines a FastAPI application with a machine-learning workflow for customer churn prediction.

## Project goals

- Maintain the existing V1 application while extending its capabilities.
- Build a reproducible machine-learning training and inference pipeline.
- Expose ML capabilities through a documented API.
- Validate application and ML behavior through automated tests.
- Package and validate the application using Docker and CI.

## Architecture

The project contains an application layer, an ML training and inference layer, automated tests, and deployment configuration.

See `docs/architecture.md` for the implementation-specific architecture.

## Prerequisites

- Python 3.12
- Git
- Docker and Docker Compose, if using the containerized setup
- PostgreSQL, if required by the selected application configuration

## Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install the dependencies specified by the project's active requirements file.
4. Configure environment variables using the documented example configuration.
5. Start any required dependencies, including PostgreSQL.

Use the actual repository commands and configuration names when completing this section.

## Machine-learning workflow

The V2 ML workflow covers dataset validation, exploratory analysis, feature engineering, preprocessing, model training, evaluation, and model serialization.

See `docs/ml-pipeline.md` for the training and inference process.

## Testing

Run the relevant test suites using the repository's documented test command.

For example:

`python -m pytest tests ml/tests -q`

## API and deployment

Document the implemented API endpoints, authentication requirements, health checks, Docker configuration, and deployment procedure.

## Security

Never commit credentials, access tokens, production database URLs, or other secrets. Load configuration from the appropriate environment or secret-management mechanism.

## Limitations

The educational churn dataset is synthetic. Evaluation results on synthetic data do not establish real-world predictive performance.

## Development status

Document completed phases, verified test results, known limitations, and outstanding work. Do not mark a feature complete until it has been implemented and tested.
