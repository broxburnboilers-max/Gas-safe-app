# Gas Safety App – West Lothian Gas Ltd

## Deploy to Netlify

### Option A – Drag & Drop (Easiest)
1. Open a terminal in this folder
2. Run: `npm install`
3. Run: `npm run build`
4. Go to https://app.netlify.com
5. Drag the `dist` folder onto the Netlify deploy area

### Option B – Netlify CLI
1. `npm install`
2. `npm run build`
3. `npm install -g netlify-cli`
4. `netlify deploy --prod`

### Option C – Connect GitHub repo
1. Push this folder to a GitHub repo
2. Log in to https://app.netlify.com
3. Click "Add new site" → "Import an existing project"
4. Connect your GitHub repo
5. Build command: `npm run build`
6. Publish directory: `dist`
7. Click Deploy

## Local Development
```
npm install
npm run dev
```
Then open http://localhost:5173


