import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Avatar } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const location = useLocation();

  return (
    <AppBar 
      position="static" 
      sx={{ 
        background: 'rgba(44, 62, 80, 0.85)',
        backdropFilter: 'blur(10px)',
        boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
        mb: 4,
        borderBottom: '1px solid rgba(255,165,0,0.5)',
        height: '70px'
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', height: '100%' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar 
            src="/kimestry_logo.png" 
            alt="Kimestry Logo" 
            sx={{ 
              width: 45, 
              height: 45,
              bgcolor: 'transparent',
              border: '1px solid rgba(255,165,0,0.3)'
            }}
          />
          <Typography 
            variant="h5" 
            component="div" 
            sx={{ 
              fontWeight: 'bold',
              color: '#ff9800',
              letterSpacing: '1px',
              textShadow: '1px 1px 2px rgba(0,0,0,0.5)'
            }}
          >
            KIMESTRY
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button 
            component={Link} 
            to="/"
            sx={{
              color: location.pathname === '/' ? '#ff9800' : '#e0e0e0',
              fontWeight: 'medium',
              '&:hover': {
                backgroundColor: 'rgba(255, 165, 0, 0.2)',
                color: '#ff9800'
              },
              textTransform: 'uppercase',
              fontSize: '0.875rem',
              px: 2,
              py: 1,
              borderRadius: '8px',
              background: location.pathname === '/' ? 'rgba(255, 165, 0, 0.2)' : 'transparent'
            }}
          >
            Leaderboard
          </Button>
          <Button 
            component={Link} 
            to="/execute"
            sx={{
              color: location.pathname === '/execute' ? '#ff9800' : '#e0e0e0',
              fontWeight: 'medium',
              '&:hover': {
                backgroundColor: 'rgba(255, 165, 0, 0.2)',
                color: '#ff9800'
              },
              textTransform: 'uppercase',
              fontSize: '0.875rem',
              px: 2,
              py: 1,
              borderRadius: '8px',
              background: location.pathname === '/execute' ? 'rgba(255, 165, 0, 0.2)' : 'transparent'
            }}
          >
            Execute
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navigation;