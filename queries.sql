-- ============================================================
--  PORTFOLIO BUILDER — PERSONAL SQL REFERENCE
--  Run these against your database using psql, TablePlus,
--  DBeaver, or the Neon dashboard query editor.
-- ============================================================


-- ============================================================
--  SELECT — VIEW DATA
-- ============================================================

-- List all users
SELECT id, email, created_at
FROM users
ORDER BY created_at DESC;

-- List all sites with their owner's email
SELECT s.id, s.subdomain, s.site_title, s.theme, s.is_published, u.email
FROM sites s
JOIN users u ON u.id = s.user_id
ORDER BY s.created_at DESC;

-- View a full profile for a specific subdomain
SELECT
    s.subdomain,
    s.site_title,
    s.theme,
    s.is_published,
    p.display_name,
    p.headline,
    p.bio,
    p.location,
    p.occupation,
    p.service_category,
    p.skills,
    p.pricing_min,
    p.pricing_max,
    p.is_remote,
    p.availability_status,
    p.is_searchable
FROM sites s
JOIN profiles p ON p.site_id = s.id
WHERE s.subdomain = 'your_subdomain_here';

-- List all links for a specific subdomain
SELECT l.id, l.label, l.url, l.icon, l.sort_order, l.is_visible
FROM links l
JOIN sites s ON s.id = l.site_id
WHERE s.subdomain = 'your_subdomain_here'
ORDER BY l.sort_order;

-- List all images for a specific subdomain
SELECT i.id, i.image_url, i.alt_text, i.caption, i.sort_order, i.is_visible
FROM images i
JOIN sites s ON s.id = i.site_id
WHERE s.subdomain = 'your_subdomain_here'
ORDER BY i.sort_order;

-- List all portfolio items for a specific subdomain
SELECT pi.id, pi.title, pi.description, pi.project_url, pi.github_url, pi.tech_stack, pi.is_visible
FROM portfolio_items pi
JOIN sites s ON s.id = pi.site_id
WHERE s.subdomain = 'your_subdomain_here'
ORDER BY pi.sort_order;

-- Count links, images, and portfolio items per site
SELECT
    s.subdomain,
    COUNT(DISTINCT l.id)  AS total_links,
    COUNT(DISTINCT i.id)  AS total_images,
    COUNT(DISTINCT pi.id) AS total_portfolio_items
FROM sites s
LEFT JOIN links          l  ON l.site_id  = s.id
LEFT JOIN images         i  ON i.site_id  = s.id
LEFT JOIN portfolio_items pi ON pi.site_id = s.id
GROUP BY s.subdomain;

-- Find all published + searchable profiles (same as the /explore directory)
SELECT s.subdomain, p.display_name, p.headline, p.location, p.availability_status
FROM sites s
JOIN profiles p ON p.site_id = s.id
WHERE s.is_published = TRUE
  AND p.is_searchable = TRUE
ORDER BY s.created_at DESC;

-- Search profiles by keyword (replace %keyword% with your search term)
SELECT s.subdomain, p.display_name, p.headline, p.skills
FROM sites s
JOIN profiles p ON p.site_id = s.id
WHERE s.is_published = TRUE
  AND (
      p.display_name ILIKE '%keyword%'
   OR p.headline     ILIKE '%keyword%'
   OR p.skills       ILIKE '%keyword%'
   OR p.occupation   ILIKE '%keyword%'
  );


-- ============================================================
--  INSERT — ADD DATA
-- ============================================================

-- Add a new link to a site (replace subdomain as needed)
INSERT INTO links (site_id, label, url, icon, sort_order, is_visible)
SELECT s.id, 'GitHub', 'https://github.com/yourname', 'github', 0, TRUE
FROM sites s
WHERE s.subdomain = 'your_subdomain_here';

-- Add a new image to a site
INSERT INTO images (site_id, image_url, alt_text, caption, sort_order, is_visible)
SELECT s.id, 'https://example.com/photo.jpg', 'A photo of my work', 'Project showcase', 0, TRUE
FROM sites s
WHERE s.subdomain = 'your_subdomain_here';

-- Add a new portfolio item to a site
INSERT INTO portfolio_items (site_id, title, description, image_url, project_url, github_url, tech_stack, sort_order, is_visible)
SELECT
    s.id,
    'My Project',
    'A short description of what this project does.',
    'https://example.com/project-image.jpg',
    'https://myproject.com',
    'https://github.com/yourname/myproject',
    'Python, Flask, PostgreSQL',
    0,
    TRUE
FROM sites s
WHERE s.subdomain = 'your_subdomain_here';


-- ============================================================
--  UPDATE — MODIFY DATA
-- ============================================================

-- Publish a site (make it publicly visible)
UPDATE sites
SET is_published = TRUE, updated_at = NOW()
WHERE subdomain = 'your_subdomain_here';

-- Unpublish a site (take it offline)
UPDATE sites
SET is_published = FALSE, updated_at = NOW()
WHERE subdomain = 'your_subdomain_here';

-- Change the theme of a site (options: light, dark, minimal, bold)
UPDATE sites
SET theme = 'dark', updated_at = NOW()
WHERE subdomain = 'your_subdomain_here';

-- Update profile information
UPDATE profiles
SET
    display_name        = 'Jane Smith',
    headline            = 'Full Stack Developer',
    bio                 = 'I build web apps with Python and React.',
    location            = 'New York, NY',
    occupation          = 'Software Engineer',
    service_category    = 'Development',
    skills              = 'Python, Flask, React, PostgreSQL',
    pricing_min         = 75.00,
    pricing_max         = 150.00,
    is_remote           = TRUE,
    availability_status = 'available',
    is_searchable       = TRUE,
    updated_at          = NOW()
WHERE site_id = (SELECT id FROM sites WHERE subdomain = 'your_subdomain_here');

-- Update a specific link's URL
UPDATE links
SET url = 'https://github.com/new-username', updated_at = NOW()
WHERE id = 1;  -- replace 1 with the actual link id

-- Hide a link without deleting it
UPDATE links
SET is_visible = FALSE, updated_at = NOW()
WHERE id = 1;

-- Hide an image without deleting it
UPDATE images
SET is_visible = FALSE
WHERE id = 1;

-- Mark a portfolio item as hidden
UPDATE portfolio_items
SET is_visible = FALSE, updated_at = NOW()
WHERE id = 1;

-- Change a user's email address
UPDATE users
SET email = 'newemail@example.com', updated_at = NOW()
WHERE email = 'oldemail@example.com';


-- ============================================================
--  DELETE — REMOVE DATA
-- ============================================================

-- Delete a specific link by id
DELETE FROM links
WHERE id = 1;  -- replace 1 with the actual link id

-- Delete all hidden links for a site
DELETE FROM links
WHERE site_id = (SELECT id FROM sites WHERE subdomain = 'your_subdomain_here')
  AND is_visible = FALSE;

-- Delete a specific image by id
DELETE FROM images
WHERE id = 1;

-- Delete a portfolio item by id
DELETE FROM portfolio_items
WHERE id = 1;

-- Delete a site and all its data (cascades to profile, links, images, portfolio items)
DELETE FROM sites
WHERE subdomain = 'your_subdomain_here';

-- Delete a user account and everything linked to it (cascades to site and all content)
DELETE FROM users
WHERE email = 'user@example.com';
