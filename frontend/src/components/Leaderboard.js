import React, { useState, useEffect } from 'react';
import axios from 'axios';
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
  Avatar,
  TextField,
  InputAdornment,
  Stack
} from '@mui/material';
import { Refresh as RefreshIcon, TrendingUp as TrendingUpIcon, Search as SearchIcon } from '@mui/icons-material';
import { Link } from 'react-router-dom';
import Navigation from './Navigation';

// Update this to match your backend server URL when running separately
const API_BASE_URL = 'http://localhost:8000/api/v1';

function Leaderboard() {
  const [benchmarkData, setBenchmarkData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Function to fetch benchmark data
  const fetchBenchmarkData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/benchmark`);
      const benchmarks = response.data.results || {};
      
      // Transform the data for the table
      const formattedData = Object.keys(benchmarks).map(name => ({
        name,
        ...benchmarks[name]
      })).sort((a, b) => b.accuracy - a.accuracy); // Sort by accuracy descending

      setBenchmarkData(formattedData);
      setFilteredData(formattedData);
      setLastUpdated(new Date().toLocaleTimeString());
      setError(null);
    } catch (err) {
      setError('Failed to fetch benchmark data. Please check your backend connection.');
      console.error('Error fetching benchmark data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch data on component mount
  useEffect(() => {
    fetchBenchmarkData();
    
    // Set up auto-refresh every 120 seconds
    const interval = setInterval(fetchBenchmarkData, 300000);
    return () => clearInterval(interval);
  }, []);

  // Handle search
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredData(benchmarkData);
    } else {
      const filtered = benchmarkData.filter(item => 
        item.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredData(filtered);
    }
  }, [searchTerm, benchmarkData]);

  // Get leading pipeline name
  const leadingPipeline = benchmarkData.length > 0 ? benchmarkData[0].name : 'None';

  return (
    <div style={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #2c3e50 0%, #34495e 50%, #3d566e 100%)',
      color: '#f5f5f5'
    }}>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Header Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sx={{ textAlign: 'center' }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography variant="h3" component="h1" gutterBottom sx={{ 
              color: '#fff', 
              textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
              fontWeight: 'bold'
            }}>
              Kimestry-Benchmark Pipeline Benchmark Leaderboard
            </Typography>
            <Typography variant="h6" sx={{ color: '#e0e0e0', mb: 2 }}>
             ahhhhhhhhhhhhhhh
            </Typography>
          </Box>
        </Grid>
      </Grid>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ 
            background: 'rgba(255, 255, 255, 0.15)',
            backdropFilter: 'blur(10px)',
            borderRadius: '15px',
            overflow: 'hidden',
            color: '#fff',
            border: '1px solid rgba(255,165,0,0.4)',
            textAlign: 'center',
            p: 3
          }}>
            <CardContent>
              <TrendingUpIcon sx={{ fontSize: 60, mb: 1, color: '#ff9800' }} />
              <Typography variant="h5" gutterBottom sx={{ color: '#f5f5f5' }}>Total Pipelines</Typography>
              <Typography variant="h2" component="div" sx={{ fontWeight: 'bold', color: '#ff9800' }}>
                {filteredData.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card sx={{ 
            background: 'rgba(255, 255, 255, 0.15)',
            backdropFilter: 'blur(10px)',
            borderRadius: '15px',
            overflow: 'hidden',
            color: '#fff',
            border: '1px solid rgba(255,165,0,0.4)',
            textAlign: 'center',
            p: 3
          }}>
            <CardContent>
              <TrendingUpIcon sx={{ fontSize: 60, mb: 1, color: '#ffa726' }} />
              <Typography variant="h5" gutterBottom sx={{ color: '#f5f5f5' }}>Leading Pipeline</Typography>
              <Typography variant="h2" component="div" sx={{ fontWeight: 'bold', color: '#ffa726' }}>
                {leadingPipeline}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Refresh Section */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <TextField
            label="Search Pipeline"
            variant="outlined"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            fullWidth
            sx={{
              backgroundColor: 'rgba(255, 255, 255, 0.15)',
              borderRadius: '10px',
              '& .MuiOutlinedInput-root': {
                color: '#fff',
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                },
                '&:hover fieldset': {
                  borderColor: '#bb86fc',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#bb86fc',
                },
              },
              '& .MuiInputLabel-root': {
                color: '#e0e0e0',
              }
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: '#bb86fc' }} />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item xs={12} md={6} sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Button
            variant="contained"
            size="large"
            onClick={fetchBenchmarkData}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} sx={{ color: '#000' }} /> : <RefreshIcon sx={{ color: '#000' }} />}
            sx={{
              backgroundColor: '#ff9800',
              color: '#000',
              '&:hover': {
                backgroundColor: '#ffa726',
              },
              boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
              flex: 1,
              fontWeight: 'bold'
            }}
          >
            {loading ? 'Refreshing...' : 'Refresh Leaderboard'}
          </Button>
          
          {lastUpdated && (
            <Typography variant="body2" sx={{ color: '#bb86fc', whiteSpace: 'nowrap' }}>
              Last updated: {lastUpdated}
            </Typography>
          )}
        </Grid>
      </Grid>

      {/* Error Message */}
      {error && (
        <Grid item xs={12} sx={{ mb: 2 }}>
          <Alert severity="error" sx={{ borderRadius: '10px' }}>
            {error}
          </Alert>
        </Grid>
      )}

      {/* Leaderboard Table */}
      <Grid item xs={12}>
        <Paper sx={{ 
          background: 'rgba(255, 255, 255, 0.15)', 
          backdropFilter: 'blur(10px)', 
          borderRadius: '15px',
          overflow: 'hidden',
          border: '1px solid rgba(255,165,0,0.4)'
        }}>
          <TableContainer>
            <Table sx={{ minWidth: 650 }} aria-label="benchmark leaderboard">
              <TableHead>
                <TableRow sx={{ backgroundColor: 'rgba(255, 165, 0, 0.3)' }}>
                  <TableCell sx={{ color: '#f5f5f5', fontWeight: 'bold' }}>Rank</TableCell>
                  <TableCell sx={{ color: '#f5f5f5', fontWeight: 'bold' }}>Pipeline Name</TableCell>
                  <TableCell align="center" sx={{ color: '#f5f5f5', fontWeight: 'bold' }}>Accuracy</TableCell>
                  <TableCell align="center" sx={{ color: '#f5f5f5', fontWeight: 'bold' }}>Schema Accuracy</TableCell>
                  <TableCell align="center" sx={{ color: '#f5f5f5', fontWeight: 'bold'}}>Total Tests</TableCell>
                  <TableCell align="center" sx={{ color: '#f5f5f5', fontWeight: 'bold' }}>Wrong Matches</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <CircularProgress sx={{ color: '#ff9800' }} />
                    </TableCell>
                  </TableRow>
                ) : filteredData.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ color: '#f5f5f5' }}>
                      No benchmark data available
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredData.map((row, index) => (
                    <TableRow
                      key={row.name}
                      sx={{
                        '&:nth-of-type(odd)': { backgroundColor: 'rgba(255, 255, 255, 0.1)' },
                        '&:nth-of-type(even)': { backgroundColor: 'rgba(255, 255, 255, 0.05)' },
                        '&:hover': { backgroundColor: 'rgba(255, 165, 0, 0.2)' },
                        cursor: 'pointer'
                      }}
                      component={Link}
                      to={`/pipeline/${row.name}`}
                    >
                      <TableCell component="th" scope="row" sx={{ color: '#f5f5f5' }}>
                        <Chip 
                          label={`#${index + 1}`}
                          size="small"
                          sx={{ 
                            backgroundColor: index === 0 ? '#FFD700' : index === 1 ? '#C0C0C0' : index === 2 ? '#CD7F32' : 'rgba(255,165,0,0.4)',
                            color: index < 3 ? '#000' : '#f5f5f5',
                            fontWeight: 'bold'
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ color: '#f5f5f5', fontWeight: 'medium' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ 
                            bgcolor: index === 0 ? '#FFD700' : index === 1 ? '#C0C0C0' : index === 2 ? '#CD7F32' : '#ff9800',
                            width: 24, 
                            height: 24, 
                            fontSize: 12,
                            mr: 1
                          }}>
                            {row.name.charAt(0)}
                          </Avatar>
                          {row.name}
                        </Box>
                      </TableCell>
                      <TableCell align="center">
                        <Chip 
                          label={`${row.accuracy ? (row.accuracy * 100).toFixed(1) : 0}%` } 
                          size="small"
                          sx={{ 
                            backgroundColor: row.accuracy > 0.8 ? '#81C784' : 
                                             row.accuracy > 0.5 ? '#ffa726' : '#EF9A9A',
                            color: '#fff',
                            fontWeight: 'bold'
                          }}
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Chip 
                          label={`${row.schema_accuracy ? (row.schema_accuracy * 100).toFixed(1) : 0}%`} 
                          size="small"
                          sx={{ 
                            backgroundColor: row.schema_accuracy > 0.8 ? '#81C784' : 
                                             row.schema_accuracy > 0.5 ? '#ffa726' : '#EF9A9A',
                            color: '#fff',
                            fontWeight: 'bold'
                          }}
                        />
                      </TableCell>
                      <TableCell align="center" sx={{ color: '#f5f5f5' }}>
                        {row.total_tests || 0}
                      </TableCell>
                      <TableCell align="center">
                        {row.wrong_matches ? (
                          <Chip 
                            label={row.wrong_matches.length} 
                            size="small"
                            sx={{ 
                              backgroundColor: '#EF9A9A',
                              color: '#fff',
                              fontWeight: 'bold'
                            }}
                          />
                        ) : (
                          <Chip 
                            label="N/A" 
                            size="small"
                            sx={{ 
                              backgroundColor: 'rgba(255,165,0,0.4)',
                              color: '#f5f5f5'
                            }}
                          />
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Grid>
    </Container>
    </div>
  );
}

export default Leaderboard;