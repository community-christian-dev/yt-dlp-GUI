# yt-dlp-GUI
A lightweight, threaded Python GUI wrapper for [yt-dlp](https://github.com/yt-dlp/yt-dlp). This tool allows users to queue multiple video downloads with custom parameters (filenames, referers, directories) and processes them sequentially with real-time progress tracking.

## Features
- **Batch Queuing:** Add multiple videos to a download queue while downloads are in progress.
- **Non-Blocking UI:** Runs downloads in a separate thread so the interface remains responsive.
- **Real-Time Progress:** Parses ```yt-dlp``` output to display a live progress bar.
- **Custom Metadata:** Easy inputs for:
  - Referer URL
  - Custom Filenames
  - Target Directory
- **Safety:** Uses ```subprocess``` securely to prevent shell injection vulnerabilities.

## Prerequisites
Before running this script, ensure you have the following installed:
1. **Python 3.x:** [Download Here](https://www.python.org/downloads/)
2. **yt-dlp:** The core engine must be installed and added to your system PATH
3. **FFmpeg:** [Download Here](https://ffmpeg.org/download.html)

_(If you need help installing ```yt-dlp``` and ```FFmpeg``` properly, I've found [this Reddit thread](https://www.reddit.com/r/youtubedl/comments/qzqzaz/can_someone_please_post_a_simple_guide_on_making/) helpful.)_

## TODO
- Format selection
- Queue persistence
- Drag & drop
- Resolution selector
- Cancel button
- Theme support

## Contributions Are Welcome
1. Fork the project
2. Create your feature branch (```git checkout -b feature/AmazingFeature```)
3. Commit your changes (```git commit -m 'Add some AmazingFeature```)
4. Push to the branch (```git push origin feature/AmazingFeature```)
5. Open a Pull Request

## Disclaimer
This project is a Graphical User Interface (GUI) wrapper for ```yt-dlp```. It is intended for archiving public media or content you have permission to download. The developers of this repository are not responsible for any misuse of this software or violations of Third Party Terms of Service.

## License
Distributed under the GNU General Public License v3.0. See ```LICENSE``` for more information.
