## Hi there 👋

<!--
**TheGlitchedMapCreator/TheGlitchedMapCreator** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- 🔭 I’m currently working on ...
- 🌱 I’m currently learning ...
- 👯 I’m looking to collaborate on ...
- 🤔 I’m looking for help with ...
- 💬 Ask me about ...
- 📫 How to reach me: ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...
-->

## Meshy banana generator

Run `generate_banana_meshy.py` with Python 3.10 or newer. It creates a textured banana model and saves it as `banana.glb` in the same folder.

You can set the `MESHY_API_KEY` environment variable before running the script. If it is not set, the script asks for your key with hidden input. Keep API keys private and do not commit them to GitHub. For a second computer, a separate Meshy key makes usage easier to track and revoke independently.

```powershell
py -3 generate_banana_meshy.py
```

The script uses only Python's standard library.