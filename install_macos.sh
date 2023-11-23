# Install the requirements from requirements.txt
if [[ -f requirements.txt ]]; then
    echo "Installing requirements from requirements.txt..."
    pip3 install -r requirements.txt
else
    echo "Error: requirements.txt not found."
    exit 1
fi

# Define the file path for the api key
file_path="$HOME/.config/openai.apikey"

# Check if the file already exists
if [[ -f $file_path ]]; then
    echo "API key file already exists at $file_path"
else
    # Prompt the user for their API key
    echo "Please enter your OpenAI API key:"
    read api_key

    # Check if the input is empty
    if [[ -z "$api_key" ]]; then
        echo "API key cannot be empty."
        exit 1
    fi

    # Check if the ~/.config directory exists and create it if not
    if [[ ! -d ~/.config ]]; then
        mkdir -p ~/.config
    fi

    # Store the API key in the specified file
    echo "$api_key" > ~/.config/openai.apikey

    # Display a success message
    echo "API key stored successfully in ~/.config/openai.apikey"
fi

echo "This will need SUDO permissions"
# Make the proofreader.py script executable
sudo cp -R ./ /usr/local/bin/mylittleproofreader

# Check if /usr/local/bin is in the PATH
if [[ ":$PATH:" == *":/usr/local/bin:"* ]]; then
    # Create a symbolic link to proofreader.py
    sudo ln -s "/usr/local/bin/mylittleproofreader/proofreader.py" /usr/local/bin/proofread
    echo "You can now run the proofreader using the command 'proofread'"
else
    echo "Error: /usr/local/bin is not in the PATH."
    exit 1
fi

PYTHON_PATH=$(which python3)
echo "Python Path: $PYTHON_PATH"

# Install automater workflows
install_workflow() {
    local workflow_name=$1

    # Check if the workflow name is provided
    if [ -z "$workflow_name" ]; then
        echo "No workflow name provided."
        return 1
    fi

    # Copy the workflow to the user's Library/Services directory
    cp -R "macos/$workflow_name.workflow" "/Users/$(whoami)/Library/Services"

    # Replace the placeholder with the actual PYTHON_PATH
    sed -e "s|PYTHON_PATH|${PYTHON_PATH}|g" "macos/$workflow_name.workflow/Contents/document.wflow" > "/Users/$(whoami)/Library/Services/$workflow_name.workflow/Contents/document.wflow"

    echo "Installed at /Users/$(whoami)/Library/Services/$workflow_name.workflow"
}

install_workflow "Evaluate"
install_workflow "Improve"
install_workflow "Proofread"
install_workflow "Simplify"
install_workflow "WriteLikeNative"
echo "Use with $workflow_name in command line or right-click, then Services, $workflow_name"