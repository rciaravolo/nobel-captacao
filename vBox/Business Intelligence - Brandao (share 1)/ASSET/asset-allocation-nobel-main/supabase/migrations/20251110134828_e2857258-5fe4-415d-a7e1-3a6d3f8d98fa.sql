-- Enable RLS on the new table
ALTER TABLE "Asset Allocation - 11.2025" ENABLE ROW LEVEL SECURITY;

-- Create policy to allow public read access
CREATE POLICY "Allow public read access to Asset Allocation - 11.2025"
ON "Asset Allocation - 11.2025"
FOR SELECT
TO public
USING (true);