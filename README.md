# TikTok Video Automator: YouTube to TikTok Video Publisher

This project automates the process of downloading a YouTube video, splitting it into 1-minute fragments, and publishing the fragments on TikTok using Selenium. The script handles Google login, publishes the first 5 fragments immediately, and schedules the remaining fragments for future daily uploads (5 fragments per day).

## Features

- **YouTube Video Download**: Downloads a video from YouTube using `yt-dlp`.
- **Video Splitting**: Splits the downloaded video into 1-minute fragments and stores them in a subdirectory.
- **TikTok Auto-Publishing**: Automatically logs in to TikTok using Google and publishes the first 5 fragments.
- **Scheduled Uploads**: Schedules the next 5 fragments for daily uploads until all fragments are published.
- **Customizable Timing**: The daily uploads are set for 9:00 AM but can be modified.

## Requirements

To run this project, you need the following tools and libraries:

### Python Libraries

Install the required libraries using `pip`:

```bash
pip install selenium yt-dlp moviepy
