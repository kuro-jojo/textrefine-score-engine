FROM openjdk:17-slim

WORKDIR /app

# Install Python3 and pip
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create and activate Python virtual environment
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --only-binary :all: -r requirements.txt

# Install remaining packages that need to be built from source
RUN pip install --no-cache-dir --no-binary :all: -r requirements.txt

# Install spacy model
RUN python3 -m spacy download en_core_web_sm

# Download and install LanguageTool
RUN apt-get update && apt-get install -y wget unzip 
RUN wget https://internal1.languagetool.org/snapshots/LanguageTool-latest-snapshot.zip
RUN mkdir -p /opt/language_tool_python
RUN unzip LanguageTool-latest-snapshot.zip -d /opt/language_tool_python
RUN rm -rf LanguageTool-latest-snapshot.zip
RUN rm -rf /var/lib/apt/lists/*

ENV ORIGINS="http://localhost:4200"
ENV LTP_PATH="/opt/language_tool_python"

# Copy the rest of the application
COPY . .

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
