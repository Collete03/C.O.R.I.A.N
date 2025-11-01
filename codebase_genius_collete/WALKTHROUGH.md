Codebase Genius - Walkthrough

This guide provides a step-by-step walkthrough of how to run the Codebase Genius application and generate documentation for a sample repository.

Prerequisites

Repository Cloned: You have cloned the main repository and are in the codebase_genius_collete directory.

Environment Activated: You have activated the Python virtual environment (e.g., source codebasejac-env/bin/activate).

Dependencies Installed: You have installed all required dependencies by running pip install -r requirements.txt.

How to Run

The system runs in two separate terminals.

Step 1: Start the Backend API Server

First, we start the FastAPI server, which waits for requests from the frontend.

Open your first terminal.

Make sure you are in the codebase_genius_collete root directory.

Run the following command:

uvicorn server:app --reload


You should see output indicating the server is running on http://127.0.0.1:8000.

(c:\Users\PC\OneDrive\Pictures\Screenshots\Screenshot 2025-step 1.jpg)



Step 2: Start the Frontend UI

Next, we start the Streamlit web application.

Open a second, new terminal.

Make sure you are in the codebase_genius_collete root directory and your virtual environment is activated here as well.

Run the following command:

streamlit run frontend/app.py


This should automatically open your web browser to http://localhost:8501.

(c:\Users\PC\OneDrive\Pictures\Screenshots\Screenshot 2025-step 2.jpg)

Generating Documentation

Now you can use the application to generate a report.

Step 3: Use the Application

In your browser (at http://localhost:8501), you will see the Codebase Genius home page.

Navigate to the "📚 Generate Docs" page using the sidebar.

In the text box, paste the URL of a public GitHub repository. For this demo, you can use the one the app was tested on:
https://github.com/Collete03/C.O.R.I.A.N

(c:\Users\PC\OneDrive\Pictures\Screenshots\Screenshot 2025-step 3.jpg )

Step 4: View the Result

Click the "🚀 Generate Documentation" button.

You will see a progress bar and status updates as the system works. In the background, your FastAPI server is running the Jac agents to clone, analyze, and generate the report.

After a few moments, the application will display the final, fully-generated Markdown documentation directly on the page.

(c:\Users\PC\OneDrive\Pictures\Screenshots\Screenshot 2025-step 4..jpg
c:\Users\PC\OneDrive\Pictures\Screenshots\Screenshot 2025-step 4.jpg 
c:\Users\PC\OneDrive\Pictures\Screenshots\Screenshot 2025-step 4b.jpg 
c:\Users\PC\OneDrive\Pictures\Screenshots\Screenshot 2025-step 4c.jpg 
c:\Users\PC\OneDrive\Pictures\Screenshots\Screenshot 2025-step 4d.jpg 
c:\Users\PC\OneDrive\Pictures\Screenshots\Screenshot 2025-step 4e.jpg)
