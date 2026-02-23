# Managing storage for cropped images

When you're saving a lot of cropped images, use **cloud storage** so the server (e.g. Render) doesn't run out of disk. The API returns URLs from the first configured option below.

---

## 1. Server disk (avoid for “a lot”)

- **Local save**: Controlled by `SAVE_LOCAL` (default `true`). Set **`SAVE_LOCAL=false`** on Render so cropped images are **not** written to the server. Response URLs will come from ImgBB, Cloudinary, or base64.
- **Cleanup**: Job dirs under `OUTPUT_DIR` are deleted when older than **`CROP_JOB_MAX_AGE_MINUTES`** (default `60`). Set to `0` to disable. Keeps disk from growing if you ever enable local save.

**Recommended on Render:** `SAVE_LOCAL=false` and at least one of ImgBB or Cloudinary configured.

---

## 2. ImgBB (good for moderate volume)

- **Setup**: Get a key at [api.imgbb.com](https://api.imgbb.com), set **`IMGBB_API_KEY`** in Render.
- **Limits**: Free tier ~32 uploads/hour. For more, check their paid plans.
- **Use case**: Moderate traffic; simple setup.

---

## 3. Cloudinary (good for moderate volume)

- **Setup**: Create a cloud at [cloudinary.com](https://cloudinary.com). In Render set:
  - `CLOUDINARY_CLOUD_NAME`
  - `CLOUDINARY_API_KEY`
  - `CLOUDINARY_API_SECRET`
- **Limits**: Free tier has monthly storage and bandwidth limits; paid tiers for more.
- **Use case**: Moderate volume; images stored in your Cloudinary account.

---

## 4. “A lot” of images (S3 / R2 / GCS)

For high volume, use your own bucket (AWS S3, Cloudflare R2, or Google Cloud Storage). The app does **not** include S3/R2 upload yet; you have two options:

**A) Client-side upload**  
- API returns cropped images as **base64** in the response (when neither ImgBB nor Cloudinary is configured).  
- Your frontend or another service decodes base64 and uploads to S3/R2.  
- Downsides: larger JSON payloads and more work on the client.

**B) Add server-side S3/R2**  
- Add a small upload path in the API (e.g. using `boto3` for S3 or R2’s S3-compatible API).  
- Set env vars such as `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_BUCKET`, `AWS_REGION` (or R2 endpoint).  
- Then the API can upload each cropped image to the bucket and return the object URL.

---

## Env summary

| Env var | Purpose |
|--------|--------|
| `SAVE_LOCAL` | `false` = don’t write crops to server disk (recommended on Render). |
| `CROP_JOB_MAX_AGE_MINUTES` | Delete local job dirs older than N minutes; `0` = disable. |
| `IMGBB_API_KEY` | Use ImgBB for image URLs. |
| `CLOUDINARY_*` | Use Cloudinary for image URLs. |

With **`SAVE_LOCAL=false`** and **ImgBB or Cloudinary** set, the server only streams crops to the chosen provider and returns their URLs; it doesn’t store them locally, so you can scale to many images without filling Render’s disk.
