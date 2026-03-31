-- Create RLS policy for Asset Allocation table to allow public read access
CREATE POLICY "Allow public read access to Asset Allocation" 
ON public."Asset Allocation" 
FOR SELECT 
USING (true);