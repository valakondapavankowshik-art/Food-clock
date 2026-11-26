# FoodClock
Every minute. Every meal. Matters.

Solo student hackathon prototype for deadline-aware food rescue. Fictional data; no actual dispatch or food safety certification.

## Run locally
```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
## Deploy
Create a public GitHub repository, upload these files (not the ZIP), then open https://share.streamlit.io/ and create an app using your repository, main branch and app.py. Copy the deployed URL into Devpost.
## How it works
Eligible donor–recipient pairs must satisfy handling compatibility, donor confirmation, recipient availability and deadline minus estimated travel and buffer >= 0. Integer linear programming maximizes allocated meals under supply and recipient demand/capacity limits. A second pass minimizes a combined travel and urgency cost without reducing allocated meals. The nearest-first baseline is greedy in batch listing order. The simulator recomputes allocations under delays, elapsed time and recipient outages. Coordinates and travel times are fictional estimates; food clocks are scenario-relative, not live. Session state resets when the session ends; no persistent database or authentication.
## Tests
Run `python -m unittest -v`.
## Limitations
No GPS, actual delivery, shared database, verified food safety, or live temperature measurements. Planned meals are not meals actually delivered. Independent trips and no fleet limits are assumed.
## AI disclosure
ChatGPT assisted with brainstorming, implementation, tests and documentation. The student should review, run, understand and customize the code before submission.

## Version 2 demo
The fictional scenario yields 250 optimized versus 170 nearest-first planned meals at default settings. Includes a network diagram, unallocated-meal explanations and removal controls. These are simulated planning outputs.

## V3 interface

Operations console with top navigation, network visualization, deadline monitor, dispatch recommendations, optimization comparison and scenario lab. Data remains fictional and session-only. Upload the hidden `.streamlit/config.toml` as well as the Python files for the intended theme.
