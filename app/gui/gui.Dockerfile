FROM python:3.12-slim

# Set working directory
WORKDIR /src

# Copy requirements file for GUI
COPY requirements.txt ./

# Install GUI dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the GUI application code and necessary files
COPY src/ ./src/

# Configure Streamlit
RUN mkdir -p /root/.streamlit
RUN echo "\
[server]\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
" > /root/.streamlit/config.toml

# Expose port for Streamlit
EXPOSE 8501

# Start Streamlit server
CMD ["streamlit", "run", "src/gui.py", "--server.port=8501", "--server.address=0.0.0.0"]