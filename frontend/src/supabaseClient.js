import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://tlipcjwxtzlryewkztsv.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRsaXBjand4dHpscnlld2t6dHN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY0NjAwNjIsImV4cCI6MjA2MjAzNjA2Mn0.sTCBRwnGHusnt9PugMad_nZoxhylEdmlCjNAEhEgrKE'

export const supabase = createClient(supabaseUrl, supabaseKey)
