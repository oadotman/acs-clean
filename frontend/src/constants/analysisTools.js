/**
 * Analysis Tools Configuration
 * Centralized definition of available analysis tools for AdCopySurge
 */

export const AVAILABLE_TOOLS = [
  { 
    id: 'compliance', 
    name: 'Compliance Checker', 
    icon: '🛡️',
    description: 'Checks platform compliance and advertising policies',
    category: 'safety'
  },
  { 
    id: 'legal', 
    name: 'Legal Risk Scanner', 
    icon: '⚖️',
    description: 'Scans for potential legal risks and claim issues',
    category: 'safety'
  },
  { 
    id: 'brand_voice', 
    name: 'Brand Voice Engine', 
    icon: '🎯',
    description: 'Analyzes brand voice consistency and tone',
    category: 'brand'
  },
  { 
    id: 'psychology', 
    name: 'Psychology Scorer', 
    icon: '🧠',
    description: 'Evaluates psychological triggers and persuasion techniques',
    category: 'optimization'
  },
  { 
    id: 'roi_generator', 
    name: 'ROI Copy Generator', 
    icon: '💰',
    description: 'Generates ROI-focused copy variations',
    category: 'generation'
  },
  { 
    id: 'ab_test', 
    name: 'A/B Test Generator', 
    icon: '🔬',
    description: 'Creates A/B test variations for optimization',
    category: 'generation'
  },
  { 
    id: 'industry_optimizer', 
    name: 'Industry Optimizer', 
    icon: '🎯',
    description: 'Optimizes copy for specific industry best practices',
    category: 'optimization'
  },
  { 
    id: 'performance_forensics', 
    name: 'Performance Forensics', 
    icon: '🔍',
    description: 'Deep analysis of performance factors and optimization opportunities',
    category: 'optimization'
  }
];

export const DEFAULT_ENABLED_TOOLS = ['compliance', 'legal', 'brand_voice', 'psychology'];

export const TOOL_CATEGORIES = {
  safety: {
    label: 'Safety & Compliance',
    color: 'error',
    icon: '🛡️'
  },
  brand: {
    label: 'Brand & Voice',
    color: 'primary',
    icon: '🎨'
  },
  optimization: {
    label: 'Optimization',
    color: 'success',
    icon: '📈'
  },
  generation: {
    label: 'Generation',
    color: 'warning',
    icon: '✨'
  }
};

// Utility functions
export const getToolById = (toolId) => {
  return AVAILABLE_TOOLS.find(tool => tool.id === toolId);
};

export const getToolsByCategory = (category) => {
  return AVAILABLE_TOOLS.filter(tool => tool.category === category);
};

export const validateToolSelection = (selectedTools) => {
  const validTools = selectedTools.filter(toolId => 
    AVAILABLE_TOOLS.some(tool => tool.id === toolId)
  );
  
  return {
    isValid: validTools.length > 0,
    validTools,
    invalidTools: selectedTools.filter(toolId => !validTools.includes(toolId))
  };
};
