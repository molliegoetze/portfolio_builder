-- Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Sites table
CREATE TABLE IF NOT EXISTS sites (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    site_title VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE,
    theme VARCHAR(50) DEFAULT 'light',
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Profiles table (extended with directory/search fields)
CREATE TABLE IF NOT EXISTS profiles (
    id BIGSERIAL PRIMARY KEY,
    site_id BIGINT NOT NULL UNIQUE REFERENCES sites(id) ON DELETE CASCADE,
    display_name VARCHAR(255),
    headline VARCHAR(255),
    bio TEXT,
    profile_image_url TEXT,
    background_image_url TEXT,
    contact_email VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255),
    occupation VARCHAR(255),
    service_category VARCHAR(100),
    subcategory VARCHAR(100),
    skills TEXT,
    pricing_min DECIMAL(10,2),
    pricing_max DECIMAL(10,2),
    is_remote BOOLEAN DEFAULT FALSE,
    availability_status VARCHAR(50) DEFAULT 'available',
    is_searchable BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Links table
CREATE TABLE IF NOT EXISTS links (
    id BIGSERIAL PRIMARY KEY,
    site_id BIGINT NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    label VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    icon VARCHAR(50),
    sort_order INT NOT NULL DEFAULT 0,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Images table
CREATE TABLE IF NOT EXISTS images (
    id BIGSERIAL PRIMARY KEY,
    site_id BIGINT NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    alt_text VARCHAR(255),
    caption TEXT,
    sort_order INT NOT NULL DEFAULT 0,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Portfolio items table
CREATE TABLE IF NOT EXISTS portfolio_items (
    id BIGSERIAL PRIMARY KEY,
    site_id BIGINT NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    image_url TEXT,
    project_url TEXT,
    github_url TEXT,
    tech_stack TEXT,
    sort_order INT NOT NULL DEFAULT 0,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
