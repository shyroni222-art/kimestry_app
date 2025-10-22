import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Alert,
  FormControl,
  InputLabel,
  Input,
  FormHelperText
} from '@mui/material';
import { Upload as UploadIcon } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const ExecutionPage = () => {
  // Pipeline execution states
  const [pipelineForm, setPipelineForm] = useState({
    file: null,
    pipelineName: '',
    envId: 'default_env',
    pipelineRoute: '',
    timeout: 600
  });
  
  // Benchmark execution states
  const [benchmarkForm, setBenchmarkForm] = useState({
    pipelineName: '',
    pipelineRoute: '',
    timeout: 600
  });

  // Results and status
  const [pipelineResult, setPipelineResult] = useState(null);
  const [benchmarkResult, setBenchmarkResult] = useState(null);
  const [pipelineLoading, setPipelineLoading] = useState(false);
  const [benchmarkLoading, setBenchmarkLoading] = useState(false);
  const [error, setError] = useState('');

  // Handle file selection for pipeline
  const handleFileChange = (e) => {
    setPipelineForm(prev => ({
      ...prev,
      file: e.target.files[0]
    }));
  };

  // Handle pipeline form changes
  const handlePipelineChange = (e) => {
    const { name, value } = e.target;
    setPipelineForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle benchmark form changes
  const handleBenchmarkChange = (e) => {
    const { name, value } = e.target;
    setBenchmarkForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Execute pipeline
  const executePipeline = async (e) => {
    e.preventDefault();
    setPipelineLoading(true);
    setError('');
    setPipelineResult(null);

    if (!pipelineForm.file) {
      setError('Please select a file to upload');
      setPipelineLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append('file', pipelineForm.file);
    formData.append('pipeline_name', pipelineForm.pipelineName);
    formData.append('env_id', pipelineForm.envId);
    formData.append('pipeline_route', pipelineForm.pipelineRoute);
    formData.append('timeout', pipelineForm.timeout);

    try {
      const response = await axios.post(`${API_BASE_URL}/pipeline/run`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setPipelineResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error executing pipeline');
      console.error('Pipeline execution error:', err);
    } finally {
      setPipelineLoading(false);
    }
  };

  // Execute benchmark
  const executeBenchmark = async (e) => {
    e.preventDefault();
    setBenchmarkLoading(true);
    setError('');
    setBenchmarkResult(null);

    const formData = new FormData();
    formData.append('pipeline_name', benchmarkForm.pipelineName);
    formData.append('pipeline_route', benchmarkForm.pipelineRoute);
    formData.append('timeout', benchmarkForm.timeout);

    try {
      const response = await axios.post(`${API_BASE_URL}/benchmark`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setBenchmarkResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error executing benchmark');
      console.error('Benchmark execution error:', err);
    } finally {
      setBenchmarkLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center" sx={{ 
        color: '#fff', 
        textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
        fontWeight: 'bold',
        mb: 4
      }}>
        Pipeline & Benchmark Execution
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: '10px' }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={4}>
        {/* Pipeline Execution Card */}
        <Grid item xs={12} lg={6}>
          <Card sx={{ 
            background: 'rgba(255, 255, 255, 0.15)',
            backdropFilter: 'blur(10px)',
            borderRadius: '15px',
            overflow: 'hidden',
            color: '#fff',
            border: '1px solid rgba(255,165,0,0.4)'
          }}>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', color: '#f5f5f5', mb: 2 }}>
                Run Pipeline
              </Typography>
              <form onSubmit={executePipeline}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <FormControl fullWidth>
                    <InputLabel htmlFor="file-upload" sx={{ color: '#f5f5f5', '&.Mui-focused': { color: '#ff9800' } }}>
                      Upload Excel File
                    </InputLabel>
                    <Input
                      id="file-upload"
                      type="file"
                      inputProps={{ accept: '.xlsx,.xls' }}
                      onChange={handleFileChange}
                      sx={{ 
                        color: '#f5f5f5',
                        '& .MuiInputBase-input': {
                          color: '#f5f5f5'
                        }
                      }}
                    />
                    <FormHelperText sx={{ color: '#f5f5f5' }}>Upload an Excel file (.xlsx or .xls)</FormHelperText>
                  </FormControl>

                  <TextField
                    name="pipelineName"
                    label="Pipeline Name"
                    value={pipelineForm.pipelineName}
                    onChange={handlePipelineChange}
                    variant="outlined"
                    fullWidth
                    required
                    InputLabelProps={{ sx: { color: '#f5f5f5' } }}
                    InputProps={{ 
                      sx: { 
                        color: '#f5f5f5',
                        backgroundColor: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: '4px'
                      } 
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '& fieldset': {
                          borderColor: 'rgba(255,165,0,0.3)',
                        },
                        '&:hover fieldset': {
                          borderColor: '#ff9800',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#ff9800',
                        },
                      }
                    }}
                  />

                  <TextField
                    name="envId"
                    label="Environment ID"
                    value={pipelineForm.envId}
                    onChange={handlePipelineChange}
                    variant="outlined"
                    fullWidth
                    InputLabelProps={{ sx: { color: '#f5f5f5' } }}
                    InputProps={{ 
                      sx: { 
                        color: '#f5f5f5',
                        backgroundColor: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: '4px'
                      } 
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '& fieldset': {
                          borderColor: 'rgba(255,165,0,0.3)',
                        },
                        '&:hover fieldset': {
                          borderColor: '#ff9800',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#ff9800',
                        },
                      }
                    }}
                  />

                  <TextField
                    name="pipelineRoute"
                    label="Pipeline Route"
                    value={pipelineForm.pipelineRoute}
                    onChange={handlePipelineChange}
                    variant="outlined"
                    fullWidth
                    required
                    InputLabelProps={{ sx: { color: '#f5f5f5' } }}
                    InputProps={{ 
                      sx: { 
                        color: '#f5f5f5',
                        backgroundColor: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: '4px'
                      } 
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '& fieldset': {
                          borderColor: 'rgba(255,165,0,0.3)',
                        },
                        '&:hover fieldset': {
                          borderColor: '#ff9800',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#ff9800',
                        },
                      }
                    }}
                  />

                  <TextField
                    name="timeout"
                    label="Timeout (seconds)"
                    type="number"
                    value={pipelineForm.timeout}
                    onChange={handlePipelineChange}
                    variant="outlined"
                    fullWidth
                    InputLabelProps={{ sx: { color: '#f5f5f5' } }}
                    InputProps={{ 
                      sx: { 
                        color: '#f5f5f5',
                        backgroundColor: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: '4px'
                      } 
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '& fieldset': {
                          borderColor: 'rgba(255,165,0,0.3)',
                        },
                        '&:hover fieldset': {
                          borderColor: '#ff9800',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#ff9800',
                        },
                      }
                    }}
                  />

                  <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    size="large"
                    disabled={pipelineLoading}
                    startIcon={<UploadIcon />}
                    sx={{
                      backgroundColor: '#ff9800',
                      color: '#000',
                      '&:hover': {
                        backgroundColor: '#ffa726',
                      },
                      fontWeight: 'bold',
                      py: 1.5,
                      mt: 1
                    }}
                  >
                    {pipelineLoading ? 'Running Pipeline...' : 'Execute Pipeline'}
                  </Button>
                </Box>
              </form>

              {pipelineResult && (
                <Box sx={{ mt: 3, p: 2, backgroundColor: 'rgba(0, 0, 0, 0.2)', borderRadius: '10px', overflowX: 'auto' }}>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#f5f5f5', mb: 1 }}>
                    Pipeline Result:
                  </Typography>
                  <pre style={{ 
                    color: '#f5f5f5', 
                    textAlign: 'left', 
                    overflowX: 'auto', 
                    maxHeight: '300px',
                    background: 'rgba(0, 0, 0, 0.3)',
                    padding: '10px',
                    borderRadius: '5px',
                    whiteSpace: 'pre-wrap',
                    wordWrap: 'break-word'
                  }}>
                    {JSON.stringify(pipelineResult, null, 2)}
                  </pre>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Benchmark Execution Card */}
        <Grid item xs={12} lg={6}>
          <Card sx={{ 
            background: 'rgba(255, 255, 255, 0.15)',
            backdropFilter: 'blur(10px)',
            borderRadius: '15px',
            overflow: 'hidden',
            color: '#fff',
            border: '1px solid rgba(255,165,0,0.4)'
          }}>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', color: '#f5f5f5', mb: 2 }}>
                Run Benchmark
              </Typography>
              <form onSubmit={executeBenchmark}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <TextField
                    name="pipelineName"
                    label="Pipeline Name"
                    value={benchmarkForm.pipelineName}
                    onChange={handleBenchmarkChange}
                    variant="outlined"
                    fullWidth
                    required
                    InputLabelProps={{ sx: { color: '#f5f5f5' } }}
                    InputProps={{ 
                      sx: { 
                        color: '#f5f5f5',
                        backgroundColor: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: '4px'
                      } 
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '& fieldset': {
                          borderColor: 'rgba(255,165,0,0.3)',
                        },
                        '&:hover fieldset': {
                          borderColor: '#ff9800',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#ff9800',
                        },
                      }
                    }}
                  />

                  <TextField
                    name="pipelineRoute"
                    label="Pipeline Route"
                    value={benchmarkForm.pipelineRoute}
                    onChange={handleBenchmarkChange}
                    variant="outlined"
                    fullWidth
                    required
                    InputLabelProps={{ sx: { color: '#f5f5f5' } }}
                    InputProps={{ 
                      sx: { 
                        color: '#f5f5f5',
                        backgroundColor: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: '4px'
                      } 
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '& fieldset': {
                          borderColor: 'rgba(255,165,0,0.3)',
                        },
                        '&:hover fieldset': {
                          borderColor: '#ff9800',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#ff9800',
                        },
                      }
                    }}
                  />

                  <TextField
                    name="timeout"
                    label="Timeout (seconds)"
                    type="number"
                    value={benchmarkForm.timeout}
                    onChange={handleBenchmarkChange}
                    variant="outlined"
                    fullWidth
                    InputLabelProps={{ sx: { color: '#f5f5f5' } }}
                    InputProps={{ 
                      sx: { 
                        color: '#f5f5f5',
                        backgroundColor: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: '4px'
                      } 
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '& fieldset': {
                          borderColor: 'rgba(255,165,0,0.3)',
                        },
                        '&:hover fieldset': {
                          borderColor: '#ff9800',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#ff9800',
                        },
                      }
                    }}
                  />

                  <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    size="large"
                    disabled={benchmarkLoading}
                    sx={{
                      backgroundColor: '#ff9800',
                      color: '#000',
                      '&:hover': {
                        backgroundColor: '#ffa726',
                      },
                      fontWeight: 'bold',
                      py: 1.5,
                      mt: 1
                    }}
                  >
                    {benchmarkLoading ? 'Running Benchmark...' : 'Execute Benchmark'}
                  </Button>
                </Box>
              </form>

              {benchmarkResult && (
                <Box sx={{ mt: 3, p: 2, backgroundColor: 'rgba(0, 0, 0, 0.2)', borderRadius: '10px', overflowX: 'auto' }}>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#f5f5f5', mb: 1 }}>
                    Benchmark Result:
                  </Typography>
                  <pre style={{ 
                    color: '#f5f5f5', 
                    textAlign: 'left', 
                    overflowX: 'auto', 
                    maxHeight: '300px',
                    background: 'rgba(0, 0, 0, 0.3)',
                    padding: '10px',
                    borderRadius: '5px',
                    whiteSpace: 'pre-wrap',
                    wordWrap: 'break-word'
                  }}>
                    {JSON.stringify(benchmarkResult, null, 2)}
                  </pre>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ExecutionPage;