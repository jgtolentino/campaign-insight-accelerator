-- Create tables for CES monitoring
CREATE TABLE IF NOT EXISTS sensors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('OK', 'FAIL')),
  last_run TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS metric_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  accuracy DECIMAL NOT NULL,
  latency DECIMAL NOT NULL,
  throughput DECIMAL NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_status (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  status TEXT NOT NULL,
  last_trained TIMESTAMP WITH TIME ZONE NOT NULL,
  accuracy DECIMAL NOT NULL,
  latency DECIMAL NOT NULL,
  throughput DECIMAL NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS retraining_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  started_at TIMESTAMP WITH TIME ZONE NOT NULL,
  completed_at TIMESTAMP WITH TIME ZONE,
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_sensors_last_run ON sensors(last_run);
CREATE INDEX IF NOT EXISTS idx_metric_history_timestamp ON metric_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_retraining_jobs_status ON retraining_jobs(status);

-- Create RLS policies
ALTER TABLE sensors ENABLE ROW LEVEL SECURITY;
ALTER TABLE metric_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE retraining_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to sensors"
  ON sensors FOR SELECT
  USING (true);

CREATE POLICY "Allow public read access to metric_history"
  ON metric_history FOR SELECT
  USING (true);

CREATE POLICY "Allow public read access to model_status"
  ON model_status FOR SELECT
  USING (true);

CREATE POLICY "Allow public read access to retraining_jobs"
  ON retraining_jobs FOR SELECT
  USING (true);

-- Create functions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_sensors_updated_at
  BEFORE UPDATE ON sensors
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_model_status_updated_at
  BEFORE UPDATE ON model_status
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_retraining_jobs_updated_at
  BEFORE UPDATE ON retraining_jobs
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column(); 