import os
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

class DataLakeManager:
    def __init__(self):
        """
        Initializes connection settings for our Hugging Face Versioned Data Lake.
        Pulls repository configurations securely from environment variables.
        """
        self.token = os.getenv("HF_TOKEN")
        self.repo_id = os.getenv("HF_DATASET_REPO", "sunny1820f/llm-pulse-data")
        self.filename = "llm_pulse_telemetry.csv"
        self.api = HfApi()

        if not self.token:
            print("Warning: HF_TOKEN environment variable not detected. Local simulation mode active.")

    def append_and_sync(self, new_records):
        """
        Downloads existing history file, checks for duplicates, appends new inference rows,
        and pushes the updated data schema back to the Hugging Face Hub.
        """
        if not new_records:
            print("Storage manager received zero items. Skipping data sync loop.")
            return

        # Convert our newly generated batch of records into a structured pandas DataFrame
        new_df = pd.DataFrame(new_records)
        local_path = self.filename

        # Attempt to pull existing dataset file from Hugging Face for incremental updates
        if self.token:
            try:
                print(f"Downloading active telemetry history tracking file from {self.repo_id}...")
                downloaded_file = hf_hub_download(
                    repo_id=self.repo_id,
                    filename=self.filename,
                    repo_type="dataset",
                    token=self.token
                )
                base_df = pd.read_csv(downloaded_file)
                print(f"Historical trace resolved. Found {len(base_df)} archived rows.")
            except Exception:
                print("No prior historical file detected in repository. Instantiating baseline tracking logs.")
                base_df = pd.DataFrame()
        else:
            base_df = pd.DataFrame()

        # Concatenate history with incoming batch payload
        combined_df = pd.concat([base_df, new_df], ignore_index=True)

        # MLOps Engineering Best Practice: Deduplicate using the source record's unique structural ID
        initial_count = len(combined_df)
        combined_df.drop_duplicates(subset=["id"], keep="first", inplace=True)
        final_count = len(combined_df)
        
        print(f"Deduplication step eliminated {initial_count - final_count} repeated event tracks.")

        # Cache the synchronized output table layout back onto local environment disk space
        combined_df.to_csv(local_path, index=False)
        print(f"Saved synchronized table snapshot containing {final_count} total rows locally.")

        # Sync the updated file payload directly back to the cloud storage space
        if self.token:
            try:
                print(f"Pushing updated versioned database state file to Hugging Face: {self.repo_id}...")
                self.api.upload_file(
                    path_or_fileobj=local_path,
                    path_in_repo=self.filename,
                    repo_id=self.repo_id,
                    repo_type="dataset",
                    token=self.token,
                    commit_message=f"Automated execution cycle sync: Added {new_df.shape[0]} tracking logs."
                )
                print("Cloud data lake synchronization finished successfully.")
            except Exception as e:
                print(f"Failed to transmit data upload streams to Hugging Face Hub: {e}")
        else:
            print("Simulation Complete: Bypassing file upload step due to missing environment tokens.")

if __name__ == "__main__":
    # Local verification run
    test_rows = [
        {"id": "hn_999", "timestamp": "2026-07-09 16:00:00", "source": "HackerNews", "raw_text": "Is anyone else getting OpenAI token rate limits on fine-tuned models?", "target_entity": "Openai", "sentiment_label": "Negative", "sentiment_score": 0.8912}
    ]
    storage = DataLakeManager()
    storage.append_and_sync(test_rows)