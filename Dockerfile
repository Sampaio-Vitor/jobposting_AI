# Start with a Python base image
FROM python:3.9

# Set the working directory in docker
WORKDIR /

# Install necessary packages
RUN apt-get update -q && apt-get install -y -q --fix-missing --no-install-recommends \
    wget \
    unzip

# Download and install the specific version of Google Chrome
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_116.0.5845.110-1_amd64.deb
RUN dpkg -i google-chrome-stable_116.0.5845.110-1_amd64.deb; exit 0
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -f -y

# Download and unzip the provided Chromium file (if still needed)
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/linux64/chrome-linux64.zip && \
    unzip chrome-linux64.zip -d /usr/bin

# Set ChromeDriver as the WebDriver (if using Selenium with Chrome)
ENV SELENIUM_DRIVER_EXECUTABLE_PATH /usr/bin/chromedriver
ENV DISPLAY=:99

# Copy the root level important files
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on (assuming it's 5000 for Flask)
EXPOSE 5001

# Clean up the package lists
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Default command to run on container start (starting the web interface)
CMD ["python", "/src/app/app.py"]
