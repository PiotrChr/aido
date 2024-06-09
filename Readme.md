# AIDO: AI-Driven Operations

AIDO is an command-line tool that leverages machine learning to provide context-aware command suggestions and operational guidance within software development environments. By analyzing your project structure, command history, and specific user queries, AIDO intelligently suggests the most relevant commands for your current context.

## Features

- **Context-Aware Suggestions**: Tailors command suggestions based on the detailed analysis of your project's directory structure and recent command usage.
- **Project-Specific Guidance**: Offers guidance based on configuration files and documentation present within your project, such as `package.json`, `Makefile`, and `README.md`.
- **Real-Time Interaction**: Utilizes a socket-based communication system to provide real-time command suggestions directly in your terminal.

## Dependencies

AIDO relies on the following main components:

- **Python 3.6+**: Ensure you have Python installed on your system. You can download it from [Python's official website](https://www.python.org/downloads/).
- **Hugging Face Transformers**: This library is used to load and interact with the machine learning model.
- **Socket Programming**: Used for creating the daemon that communicates with the command-line interface.

## Installation

Follow these steps to install AIDO on your system:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/aido.git
   cd aido
   ```

2. **Install Required Libraries**:
    ```bash
    pip install transformers huggingface_hub
    ```

3. **Setup Environment Variables and Install**:
    ```bash
    ./install.sh
    ```

4. **Restart your terminal**:
    ```bash
    source ~/.zshrc
    ```

## Usage

Once installed, you can use AIDO directly from your command line:

```bash
aido "start my_project"
aido "deploy my_project to production"
```

### Querying AIDO

Send your query as an argument to aido followed by the action you are interested in. AIDO will process your request and provide the relevant command or guidance based on your current project context.


## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See LICENSE for more information.






