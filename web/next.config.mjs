// Static export: `next build` writes plain HTML/CSS/JS to ./out, which any
// static host can serve (GitHub Pages, Vercel, Netlify, a university server).
//
// NEXT_PUBLIC_BASE_PATH is set by the GitHub Pages workflow, because a project
// site lives under /<repo-name>/. Leave it empty for local dev or Vercel.
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  basePath,
  trailingSlash: true,
  images: { unoptimized: true },
};

export default nextConfig;
