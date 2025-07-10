# Getting Started

## Local environment

1. Install the required tools:
   * [Azure Developer CLI](https://aka.ms/azure-dev/install)
   * [Node.js](https://nodejs.org/)
   * [Python >=3.11](https://www.python.org/downloads/)
      * **Important**: Python and the pip package manager must be in the path in Windows for the setup scripts to work.
      * **Important**: Ensure you can run `python --version` from console. On Ubuntu, you might need to run `sudo apt install python-is-python3` to link `python` to `python3`.
   * [Git](https://git-scm.com/downloads)
   * [Powershell](https://learn.microsoft.com/powershell/scripting/install/installing-powershell) - For Windows users only.

2. Clone the repo
3. Proceed to the next section to [deploy the app](#deploying-the-app).

## Deploying the app

The steps below will provision Azure resources and deploy the application code to Azure Container Apps.

1. Login to your Azure account:

    ```shell
    azd auth login
    ```

1. Create a new azd environment:

    ```shell
    azd env new
    ```

    Enter a name that will be used for the resource group.
    This will create a new folder in the `.azure` folder, and set it as the active environment for any calls to `azd` going forward.

1. Run this single command to provision the resources, deploy the code, and setup integrated vectorization for the sample data:

   ```shell
   azd up
   ````

   * You will be prompted to select two locations, one for the majority of resources and one for the OpenAI resource, which is currently a short list. That location list is based on the [OpenAI model availability table](https://learn.microsoft.com/azure/ai-services/openai/concepts/models#global-standard-model-availability) and may become outdated as availability changes.

1. After the application has been successfully deployed you will see a URL printed to the console.  Navigate to that URL to interact with the app in your browser.

## Development server

You can run this app locally using either the Azure services you provisioned by following the [deployment instructions](#deploying-the-app), or by pointing the local app at already [existing services](docs/existing_services.md).

1. If you deployed with `azd up`, you should see a `app/backend/.env` file with the necessary environment variables.

2. If did *not* use `azd up`, you will need to create `app/backend/.env` file with the following environment variables:

   ```shell
   AZURE_OPENAI_ENDPOINT=wss://<your instance name>.openai.azure.com
   AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-4o-realtime-preview
   AZURE_OPENAI_REALTIME_VOICE_CHOICE=<choose one: echo, alloy, shimmer>
   AZURE_OPENAI_API_KEY=<your api key>
   AZURE_SEARCH_ENDPOINT=https://<your service name>.search.windows.net
   AZURE_SEARCH_INDEX=<your index name>
   AZURE_SEARCH_API_KEY=<your api key>
   ```

   To use Entra ID (your user when running locally, managed identity when deployed) simply don't set the keys.

3. Run this command to start the app:

   Windows:

   ```pwsh
   pwsh .\scripts\start.ps1
   ```

   Linux/Mac:

   ```bash
   ./scripts/start.sh
   ```

4. The app is available on [http://localhost:8765](http://localhost:8765).

   Once the app is running, when you navigate to the URL above you should see the start screen of the app:
   ![app screenshot](docs/talktoyourdataapp.png)


## Guidance

### Security

This template uses [Managed Identity](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview) to eliminate the need for developers to manage these credentials. Applications can use managed identities to obtain Microsoft Entra tokens without having to manage any credentials.