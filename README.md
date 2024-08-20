# Notice Downloader

This Python script enables users to download notices from the official website of [Faculty of Humanities and Social Sciences](https://fohss.tu.edu.np/notices). It utilizes web scraping techniques to extract relevant information and download PDF files.

## Getting Started

If you are new to the project, here are some initial steps to get started:

**1. Clone the project**

```
git clone https://github.com/ghanteyyy/BCA-Notice-Downloader.git
```

**2. Install Dependencies**

```
pip install -r requirements.txt
```

**3. Run the script**

```
cd scripts

python main.py
```

## Features

- Fetches notices.
- Downloads PDF files associated with the notices.
- Allows users to reveal the downloaded PDF files in the file explorer.
- Verifies if the PDF files are already downloaded to prevent duplicate downloads.

## How it Works

- The script uses web scraping techniques to extract notices from the official website of [Faculty of Humanities and Social Sciences](https://fohss.tu.edu.np/notices)
- It checks if the notices contain PDF files related to notice and downloads them if available.
- The downloaded PDF files are saved in the user's downloads directory.

## Contributing

Contributions are welcome! If you have any suggestions or improvements, feel free to open an issue or create a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
