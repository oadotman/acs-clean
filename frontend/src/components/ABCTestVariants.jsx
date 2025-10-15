import React, { useState } from 'react';
import { ContentCopy, CheckCircle, TrendingUp, ErrorOutline, People } from '@mui/icons-material';

const ABCTestVariants = ({ variants = [] }) => {
  const [copiedId, setCopiedId] = useState(null);

  const copyToClipboard = async (text, id) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const getVariantColor = (type) => {
    switch (type) {
      case 'benefit_focused':
        return 'from-green-500 to-emerald-600';
      case 'problem_focused':
        return 'from-orange-500 to-red-600';
      case 'story_driven':
        return 'from-purple-500 to-indigo-600';
      default:
        return 'from-blue-500 to-cyan-600';
    }
  };

  const getVariantIcon = (type) => {
    switch (type) {
      case 'benefit_focused':
        return <TrendingUp sx={{ fontSize: 20 }} />;
      case 'problem_focused':
        return <ErrorOutline sx={{ fontSize: 20 }} />;
      case 'story_driven':
        return <People sx={{ fontSize: 20 }} />;
      default:
        return <TrendingUp sx={{ fontSize: 20 }} />;
    }
  };

  if (!variants || variants.length === 0) {
    return null;
  }

  return (
    <div className="mt-8 space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-3">
          Strategic A/B/C Testing
        </h2>
        <p className="text-gray-400 text-lg">
          Know What Works Before You Spend
        </p>
        <p className="text-gray-500 mt-2 max-w-3xl mx-auto">
          Stop running random ad tests. Generate 3 scientifically-designed variants—each targeting different psychological triggers.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {variants.map((variant, index) => (
          <div
            key={variant.id}
            className="bg-gray-800/50 rounded-xl border border-gray-700 overflow-hidden hover:border-gray-600 transition-all duration-300 hover:shadow-xl hover:shadow-purple-500/10"
          >
            {/* Header */}
            <div className={`bg-gradient-to-r ${getVariantColor(variant.type)} p-4`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getVariantIcon(variant.type)}
                  <span className="text-white font-bold text-lg">
                    {variant.variant_label}
                  </span>
                </div>
                <button
                  onClick={() => copyToClipboard(variant.copy, variant.id)}
                  className="p-2 rounded-lg bg-white/20 hover:bg-white/30 transition-colors"
                  title="Copy variant"
                >
                  {copiedId === variant.id ? (
                    <CheckCircle sx={{ fontSize: 16, color: 'white' }} />
                  ) : (
                    <ContentCopy sx={{ fontSize: 16, color: 'white' }} />
                  )}
                </button>
              </div>
              <div className="mt-2">
                <h3 className="text-white font-semibold text-lg">
                  {variant.variant_name}
                </h3>
                <p className="text-white/80 text-sm mt-1">
                  {variant.variant_description}
                </p>
              </div>
            </div>

            {/* Content */}
            <div className="p-5 space-y-4">
              {/* Ad Copy Preview */}
              <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
                <div className="text-sm text-gray-400 mb-2">Ad Copy:</div>
                <div className="space-y-3">
                  <div>
                    <div className="text-xs text-purple-400 font-semibold mb-1">HEADLINE</div>
                    <div className="text-white font-medium">{variant.headline}</div>
                  </div>
                  <div>
                    <div className="text-xs text-purple-400 font-semibold mb-1">BODY</div>
                    <div className="text-gray-300 text-sm">{variant.body_text}</div>
                  </div>
                  <div>
                    <div className="text-xs text-purple-400 font-semibold mb-1">CTA</div>
                    <div className="text-white font-semibold">{variant.cta}</div>
                  </div>
                </div>
              </div>

              {/* Best For */}
              <div>
                <div className="text-sm font-semibold text-gray-300 mb-2 flex items-center">
                  <span className="mr-2">✓</span> Best for:
                </div>
                <ul className="space-y-1">
                  {variant.best_for && variant.best_for.map((item, idx) => (
                    <li key={idx} className="text-gray-400 text-sm flex items-start">
                      <span className="text-purple-400 mr-2">•</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Target Audience */}
              <div className="pt-3 border-t border-gray-700">
                <div className="text-xs text-gray-500 font-semibold mb-1">
                  TARGET AUDIENCE
                </div>
                <div className="text-gray-400 text-sm">
                  {variant.target_audience}
                </div>
              </div>

              {/* Emotional Trigger */}
              <div>
                <div className="text-xs text-gray-500 font-semibold mb-1">
                  EMOTIONAL TRIGGER
                </div>
                <div className="text-gray-400 text-sm">
                  {variant.emotional_trigger}
                </div>
              </div>

              {/* Psychological Framework Badge */}
              <div className="flex items-center justify-between pt-3 border-t border-gray-700">
                <span className="text-xs text-gray-500">Framework:</span>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r ${getVariantColor(variant.type)} text-white`}>
                  {variant.psychological_framework}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Testing Strategy Note */}
      <div className="mt-8 p-6 bg-gradient-to-r from-purple-900/20 to-indigo-900/20 rounded-xl border border-purple-700/30">
        <h3 className="text-lg font-semibold text-white mb-2">
          💡 Testing Strategy
        </h3>
        <p className="text-gray-300 text-sm">
          Run these three variants simultaneously with equal traffic distribution (33% each). 
          After reaching statistical significance, scale the winning variant and iterate on the 
          learnings from the other two.
        </p>
      </div>
    </div>
  );
};

export default ABCTestVariants;
