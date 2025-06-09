import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    // Create a new retraining job
    const { data: job, error: jobError } = await supabaseClient
      .from('retraining_jobs')
      .insert([
        {
          status: 'pending',
          started_at: new Date().toISOString(),
        },
      ])
      .select()
      .single();

    if (jobError) throw jobError;

    // Trigger the retraining process
    const response = await fetch(Deno.env.get('RETRAINING_WEBHOOK_URL') ?? '', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${Deno.env.get('RETRAINING_API_KEY')}`,
      },
      body: JSON.stringify({
        jobId: job.id,
        timestamp: new Date().toISOString(),
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to trigger retraining');
    }

    return new Response(
      JSON.stringify({ jobId: job.id }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      },
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      },
    );
  }
}); 