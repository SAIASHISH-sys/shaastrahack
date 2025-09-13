const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 5000;

// Allow requests from your frontend (local)
app.use(cors());

// Ensure uploads folder exists
const UPLOAD_DIR = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR);

// Multer storage config (sanitizes name a bit)
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOAD_DIR),
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname);
    const base = path.basename(file.originalname, ext).replace(/\s+/g, '-').replace(/[^\w\-]/g, '');
    cb(null, `${Date.now()}-${base}${ext}`);
  },
});

// Optional: file size limit and simple filter (5 MB and allow all types here)
const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 }, // 5 MB
  fileFilter: (req, file, cb) => {
    // If you want to limit to images only, uncomment below:
    // if (!file.mimetype.startsWith('image/')) return cb(new Error('Only images allowed'));
    cb(null, true);
  },
});

app.use('/uploads', express.static(UPLOAD_DIR));

// Upload endpoint — expects field name "file"
app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file uploaded' });
  const fileUrl = `http://localhost:${PORT}/uploads/${req.file.filename}`;
  res.json({ fileUrl, filename: req.file.filename });
});

// Simple error handler (catches Multer errors)
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) return res.status(400).json({ error: err.message });
  if (err) return res.status(500).json({ error: err.message || 'Server error' });
  next();
});

app.listen(PORT, () => console.log(`Backend running at http://localhost:${PORT}`));
