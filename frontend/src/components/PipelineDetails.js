import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  CardHeader,
  IconButton,
  Link,
  Breadcrumbs
} from '@mui/material';
import { Refresh as RefreshIcon, TrendingUp as TrendingUpIcon, ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

// Update this to match your backend server URL when running separately
const API_BASE_URL = 'http://localhost:8000/api/v1';

function PipelineDetails() {
  const { pipelineName } = useParams();
  const navigate = useNavigate();
  const [pipelineData, setPipelineData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Function to fetch pipeline data
  const fetchPipelineData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/benchmark/${pipelineName}`);
      setPipelineData(response.data.results);
      setError(null);
    } catch (err) {
      setError('Failed to fetch pipeline data. Please check your backend connection.');
      console.error('Error fetching pipeline data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPipelineData();
  }, [pipelineName]);

  // Separate correct and incorrect results
  const [correctResults, setCorrectResults] = useState([]);
  const [incorrectResults, setIncorrectResults] = useState([]);

  useEffect(() => {
    if (pipelineData && pipelineData.wrong_matches) {
      setIncorrectResults(pipelineData.wrong_matches);
    }
  }, [pipelineData]);

  const handleBack = () => {
    navigate('/');
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ borderRadius: '10px' }}>
          {error}
        </Alert>
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
          <Button 
            variant="contained" 
            onClick={handleBack}
            startIcon={<ArrowBackIcon />}
          >
            Back to Leaderboard
          </Button>
        </Box>
      </Container>
    );
  }

  if (!pipelineData) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="warning" sx={{ borderRadius: '10px' }}>
          No data available for this pipeline.
        </Alert>
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
          <Button 
            variant="contained" 
            onClick={handleBack}
            startIcon={<ArrowBackIcon />}
          >
            Back to Leaderboard
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Grid container spacing={3}>
        {/* Breadcrumbs */}
        <Grid item xs={12}>
          <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
            <Link underline="hover" color="inherit" href="/" onClick={(e) => { e.preventDefault(); navigate('/'); }}>
              Leaderboard
            </Link>
            <Typography color="text.primary">{pipelineName}</Typography>
          </Breadcrumbs>
        </Grid>

        {/* Header Section */}
        <Grid item xs={12}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography variant="h3" component="h1" gutterBottom sx={{ 
              color: '#fff', 
              textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
              fontWeight: 'bold'
            }}>
              Pipeline: {pipelineName}
            </Typography>
            <Typography variant="h6" sx={{ color: '#e0e0e0', mb: 2 }}>
              Detailed performance metrics and results analysis
            </Typography>
            
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 2 }}>
              <Button
                variant="contained"
                color="primary"
                size="large"
                onClick={fetchPipelineData}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <RefreshIcon />}
                sx={{
                  backgroundColor: '#1a237e',
                  '&:hover': {
                    backgroundColor: '#303f9f',
                  },
                  boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
                }}
              >
                {loading ? 'Refreshing...' : 'Refresh Data'}
              </Button>
              
              <Button
                variant="outlined"
                color="secondary"
                size="large"
                onClick={handleBack}
                startIcon={<ArrowBackIcon />}
                sx={{
                  color: '#bb86fc',
                  borderColor: '#bb86fc',
                  '&:hover': {
                    backgroundColor: 'rgba(187, 134, 252, 0.1)',
                    borderColor: '#bb86fc',
                  },
                  boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
                }}
              >
                Back to Leaderboard
              </Button>
            </Box>
          </Box>
        </Grid>

        {/* Stats Cards */}
        <Grid item xs={12}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Card sx={{ 
                background: 'linear-gradient(45deg, #2196F3, #21CBF3)', 
                color: 'white',
                boxShadow: '0 6px 20px rgba(33, 150, 243, 0.4)',
              }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Column+Schema Accuracy</Typography>
                  <Typography variant="h3" component="div">
                    {pipelineData.accuracy ? (pipelineData.accuracy * 100).toFixed(2) + '%' : '0%'}
                  </Typography>
                  <TrendingUpIcon sx={{ fontSize: 40, mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <Card sx={{ 
                background: 'linear-gradient(45deg, #4CAF50, #81C784)', 
                color: 'white',
                boxShadow: '0 6px 20px rgba(76, 175, 80, 0.4)',
              }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Schema Accuracy</Typography>
                  <Typography variant="h3" component="div">
                    {pipelineData.schema_accuracy ? (pipelineData.schema_accuracy * 100).toFixed(2) + '%' : '0%'}
                  </Typography>
                  <TrendingUpIcon sx={{ fontSize: 40, mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <Card sx={{ 
                background: 'linear-gradient(45deg, #FF9800, #FFB74D)', 
                color: 'white',
                boxShadow: '0 6px 20px rgba(255, 152, 0, 0.4)',
              }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Total Tests</Typography>
                  <Typography variant="h3" component="div">
                    {pipelineData.total_tests || 0}
                  </Typography>
                  <TrendingUpIcon sx={{ fontSize: 40, mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Error Message */}
        {error && (
          <Grid item xs={12}>
            <Alert severity="error" sx={{ borderRadius: '10px' }}>
              {error}
            </Alert>
          </Grid>
        )}

        {/* Wrong Matches Section */}
        <Grid item xs={12}>
          <Paper sx={{ 
            background: 'rgba(255, 255, 255, 0.1)', 
            backdropFilter: 'blur(10px)', 
            borderRadius: '15px',
            overflow: 'hidden',
            p: 2
          }}>
            <Typography variant="h5" sx={{ mb: 2, color: '#fff', fontWeight: 'bold' }}>
              Incorrect Results ({pipelineData.wrong_matches ? pipelineData.wrong_matches.length : 0})
            </Typography>
            
            {pipelineData.wrong_matches && pipelineData.wrong_matches.length > 0 ? (
              <TableContainer>
                <Table sx={{ minWidth: 650 }} aria-label="wrong matches table">
                  <TableHead>
                    <TableRow sx={{ backgroundColor: 'rgba(0, 0, 0, 0.2)' }}>
                      <TableCell sx={{ color: '#fff', fontWeight: 'bold' }}>Original Column</TableCell>
                      <TableCell sx={{ color: '#fff', fontWeight: 'bold' }}>Predicted Column</TableCell>
                      <TableCell sx={{ color: '#fff', fontWeight: 'bold' }}>Predicted Schema</TableCell>
                      <TableCell sx={{ color: '#fff', fontWeight: 'bold' }}>Expected Column</TableCell>
                      <TableCell sx={{ color: '#fff', fontWeight: 'bold' }}>Expected Schema</TableCell>
                      <TableCell sx={{ color: '#fff', fontWeight: 'bold' }}>Explanation</TableCell>
                      <TableCell sx={{ color: '#fff', fontWeight: 'bold' }}>Environment</TableCell>
                      <TableCell sx={{ color: '#fff', fontWeight: 'bold' }}>Table</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {pipelineData.wrong_matches.map((wrongMatch, index) => (
                      <TableRow
                        key={index}
                        sx={{
                          '&:nth-of-type(odd)': { backgroundColor: 'rgba(255, 255, 255, 0.05)' },
                          '&:nth-of-type(even)': { backgroundColor: 'rgba(255, 255, 255, 0.02)' },
                          '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' }
                        }}
                      >
                        <TableCell sx={{ color: '#fff' }}>{wrongMatch.original_column}</TableCell>
                        <TableCell sx={{ color: '#fff', fontWeight: 'medium' }}>
                          <Chip 
                            label={wrongMatch.predicted_fitted_column || 'N/A'} 
                            size="small"
                            sx={{ 
                              backgroundColor: '#e57373',
                              color: '#fff',
                              fontWeight: 'bold'
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ color: '#fff', fontWeight: 'medium' }}>
                          <Chip 
                            label={wrongMatch.predicted_fitted_schema || 'N/A'} 
                            size="small"
                            sx={{ 
                              backgroundColor: '#e57373',
                              color: '#fff',
                              fontWeight: 'bold'
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ color: '#fff', fontWeight: 'medium' }}>
                          <Chip 
                            label={wrongMatch.expected_fitted_column || 'N/A'} 
                            size="small"
                            sx={{ 
                              backgroundColor: '#81C784',
                              color: '#fff',
                              fontWeight: 'bold'
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ color: '#fff', fontWeight: 'medium' }}>
                          <Chip 
                            label={wrongMatch.expected_fitted_schema || 'N/A'} 
                            size="small"
                            sx={{ 
                              backgroundColor: '#81C784',
                              color: '#fff',
                              fontWeight: 'bold'
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ color: '#fff' }}>{wrongMatch.explanation}</TableCell>
                        <TableCell sx={{ color: '#fff' }}>{wrongMatch.env_id}</TableCell>
                        <TableCell sx={{ color: '#fff' }}>{wrongMatch.table_name}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Alert severity="info" sx={{ borderRadius: '10px' }}>
                No incorrect results found. All predictions were correct!
              </Alert>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default PipelineDetails;