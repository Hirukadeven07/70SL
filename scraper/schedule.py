"""
Scheduling is handled by Google Cloud Scheduler triggering the Cloud Run Job
(scraper/Dockerfile). Suggested schedule:

  ikman      → every 4 h  (0 */4 * * *)
  riyasewana → every 6 h  (30 */6 * * *)
  sarathiads → every 4 h  (15 1,5,9,13,17,21 * * *)

Each job invokes:  python -m scraper.main --source <name>
"""
