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
  CardHeader,
  Avatar,
  IconButton,
  TextField,
  InputAdornment
} from '@mui/material';
import { Refresh as RefreshIcon, TrendingUp as TrendingUpIcon, Search as SearchIcon } from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { Link } from 'react-router-dom';

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
      
      // Transform the data for the table and charts
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
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchBenchmarkData, 30000);
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

  // Prepare data for charts
  const chartData = filteredData.map(item => ({
    name: item.name,
    accuracy: item.accuracy ? parseFloat((item.accuracy * 100).toFixed(2)) : 0,
    schemaAccuracy: item.schema_accuracy ? parseFloat((item.schema_accuracy * 100).toFixed(2)) : 0,
  }));

  // Define colors for the chart bars
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Grid container spacing={3}>
        {/* Header Section */}
        <Grid item xs={12}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography variant="h2" component="h1" gutterBottom sx={{ 
              color: '#fff', 
              textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
              fontWeight: 'bold'
            }}>
              Kimestry Pipeline Benchmark Leaderboard
            </Typography>
            <Typography variant="h6" sx={{ color: '#e0e0e0', mb: 2 }}>
              Real-time performance metrics for all pipelines
            </Typography>
            
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 2, mb: 2 }}>
              <TextField
                label="Search Pipeline"
                variant="outlined"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                sx={{
                  backgroundColor: 'rgba(255, 255, 255, 0.15)',
                  borderRadius: '10px',
                  width: '300px',
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
              <Button
                variant="contained"
                color="primary"
                size="large"
                onClick={fetchBenchmarkData}
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
                {loading ? 'Refreshing...' : 'Refresh Leaderboard'}
              </Button>
              
              {lastUpdated && (
                <Typography variant="body2" sx={{ color: '#bb86fc' }}>
                  Last updated: {lastUpdated}
                </Typography>
              )}
            </Box>
          </Box>
        </Grid>

        {/* Stats Cards */}
        <Grid item xs={12}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={4}>
              <Card sx={{ 
                background: 'linear-gradient(45deg, #2196F3, #21CBF3)', 
                color: 'white',
                boxShadow: '0 6px 20px rgba(33, 150, 243, 0.4)',
              }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Total Pipelines</Typography>
                  <Typography variant="h3" component="div">{filteredData.length}</Typography>
                  <TrendingUpIcon sx={{ fontSize: 40, mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={4}>
              <Card sx={{ 
                background: 'linear-gradient(45deg, #4CAF50, #81C784)', 
                color: 'white',
                boxShadow: '0 6px 20px rgba(76, 175, 80, 0.4)',
              }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Avg. Accuracy</Typography>
                  <Typography variant="h3" component="div">
                    {filteredData.length > 0 
                      ? (filteredData.reduce((sum, item) => sum + (item.accuracy || 0), 0) / filteredData.length * 100).toFixed(2) + '%' 
                      : '0%'}
                  </Typography>
                  <TrendingUpIcon sx={{ fontSize: 40, mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={4}>
              <Card sx={{ 
                background: 'linear-gradient(45deg, #FF9800, #FFB74D)', 
                color: 'white',
                boxShadow: '0 6px 20px rgba(255, 152, 0, 0.4)',
              }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Avg. Schema Accuracy</Typography>
                  <Typography variant="h3" component="div">
                    {filteredData.length > 0 
                      ? (filteredData.reduce((sum, item) => sum + (item.schema_accuracy || 0), 0) / filteredData.length * 100).toFixed(2) + '%' 
                      : '0%'}
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

        {/* Charts Section */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 2, height: 400, background: 'rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(10px)', borderRadius: '15px' }}>
            <Typography variant="h6" sx={{ mb: 2, color: '#fff' }}>Accuracy Comparison</Typography>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="90%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} tick={{ fill: '#fff' }} />
                  <YAxis tick={{ fill: '#fff' }} domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(30, 30, 40, 0.9)', 
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '10px',
                      color: '#fff'
                    }} 
                  />
                  <Legend />
                  <Bar dataKey="accuracy" name="Column+Schema Accuracy">
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80%' }}>
                <CircularProgress />
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 2, height: 400, background: 'rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(10px)', borderRadius: '15px' }}>
            <Typography variant="h6" sx={{ mb: 2, color: '#fff' }}>Accuracy Breakdown</Typography>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="90%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} tick={{ fill: '#fff' }} />
                  <YAxis tick={{ fill: '#fff' }} domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(30, 30, 40, 0.9)', 
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '10px',
                      color: '#fff'
                    }} 
                  />
                  <Legend />
                  <Bar dataKey="schemaAccuracy" name="Schema Accuracy" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80%' }}>
                <CircularProgress />
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Leaderboard Table */}
        <Grid item xs={12}>
          <Paper sx={{ 
            background: 'rgba(255, 255, 255, 0.1)', 
            backdropFilter: 'blur(10px)', 
            borderRadius: '15px',
            overflow: 'hidden'
          }}>
            <TableContainer>
              <Table sx={{ minWidth: 650 }} aria-label="benchmark leaderboard">
                <TableHead>
                  <TableRow sx={{ backgroundColor: 'rgba(0, 0, 0, 0.2)' }}>
                    <TableCell sx={{ color: '#fff', fontWeight: 'bold' }}>Rank</TableCell>
                    <TableCell sx={{ color: '#fff', fontWeight: 'bold' }}>Pipeline Name</TableCell>
                    <TableCell align="center" sx={{ color: '#fff', fontWeight: 'bold' }}>Column+Schema Accuracy</TableCell>
                    <TableCell align="center" sx={{ color: '#fff', fontWeight: 'bold' }}>Schema Accuracy</TableCell>
                    <TableCell align="center" sx={{ color: '#fff', fontWeight: 'bold' }}>Total Tests</TableCell>
                    <TableCell align="center" sx={{ color: '#fff', fontWeight: 'bold' }}>Wrong Matches</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        <CircularProgress />
                      </TableCell>
                    </TableRow>
                  ) : filteredData.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center" sx={{ color: '#fff' }}>
                        No benchmark data available
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredData.map((row, index) => (
                      <TableRow
                        key={row.name}
                        sx={{
                          '&:nth-of-type(odd)': { backgroundColor: 'rgba(255, 255, 255, 0.05)' },
                          '&:nth-of-type(even)': { backgroundColor: 'rgba(255, 255, 255, 0.02)' },
                          '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' },
                          cursor: 'pointer'
                        }}
                        component={Link}
                        to={`/pipeline/${row.name}`}
                      >
                        <TableCell component="th" scope="row" sx={{ color: '#fff' }}>
                          <Chip 
                            label={`#${index + 1}`}
                            size="small"
                            sx={{ 
                              backgroundColor: index === 0 ? '#FFD700' : index === 1 ? '#C0C0C0' : index === 2 ? '#CD7F32' : '#555',
                              color: '#000',
                              fontWeight: 'bold'
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ color: '#fff', fontWeight: 'medium' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Avatar sx={{ 
                              bgcolor: index === 0 ? '#FFD700' : index === 1 ? '#C0C0C0' : index === 2 ? '#CD7F32' : '#42a5f5',
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
                            label={`${row.accuracy ? (row.accuracy * 100).toFixed(2) : 0}%`} 
                            size="small"
                            sx={{ 
                              backgroundColor: row.accuracy > 0.8 ? '#81C784' : 
                                               row.accuracy > 0.5 ? '#FFB74D' : '#E57373',
                              color: '#fff',
                              fontWeight: 'bold'
                            }}
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Chip 
                            label={`${row.schema_accuracy ? (row.schema_accuracy * 100).toFixed(2) : 0}%`} 
                            size="small"
                            sx={{ 
                              backgroundColor: row.schema_accuracy > 0.8 ? '#81C784' : 
                                               row.schema_accuracy > 0.5 ? '#FFB74D' : '#E57373',
                              color: '#fff',
                              fontWeight: 'bold'
                            }}
                          />
                        </TableCell>
                        <TableCell align="center" sx={{ color: '#fff' }}>
                          {row.total_tests || 0}
                        </TableCell>
                        <TableCell align="center">
                          {row.wrong_matches ? (
                            <Chip 
                              label={row.wrong_matches.length} 
                              size="small"
                              sx={{ 
                                backgroundColor: '#e57373',
                                color: '#fff',
                                fontWeight: 'bold'
                              }}
                            />
                          ) : (
                            <Chip 
                              label="N/A" 
                              size="small"
                              sx={{ 
                                backgroundColor: '#999',
                                color: '#fff'
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
      </Grid>
    </Container>
  );
}

export default Leaderboard;