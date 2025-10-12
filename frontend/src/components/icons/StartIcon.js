import React from 'react';
import { RocketLaunch } from '@mui/icons-material';

/**
 * Centralized Start Icon component
 * 
 * Replaces PlayArrow with RocketLaunch for semantic consistency.
 * This ensures all "start/generate/analyze" actions use the same icon.
 * 
 * Usage:
 *   import StartIcon from '../components/icons/StartIcon';
 *   <StartIcon />
 */
const StartIcon = (props) => {
  return <RocketLaunch {...props} />;
};

export default StartIcon;

// Named export for backwards compatibility
export { StartIcon };