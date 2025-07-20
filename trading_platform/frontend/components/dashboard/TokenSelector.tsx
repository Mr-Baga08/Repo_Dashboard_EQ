'use client';

import { useState, useEffect, useCallback } from 'react';
import { useDashboardStore } from '@/lib/store/useDashboardStore';

interface Token {
  id: number;
  symbol: string;
  exchange: string;
  description: string;
}

// A simple debounce function
function debounce<F extends (...args: any[]) => any>(func: F, waitFor: number) {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<F>): Promise<ReturnType<F>> =>
    new Promise(resolve => {
      if (timeout) {
        clearTimeout(timeout);
      }
      timeout = setTimeout(() => resolve(func(...args)), waitFor);
    });
}

export default function TokenSelector() {
  const { tradeConfig, setTradeConfig } = useDashboardStore();
  const [query, setQuery] = useState(tradeConfig.tokenSymbol);
  const [results, setResults] = useState<Token[]>([]);
  const [isDropdownVisible, setIsDropdownVisible] = useState(false);

  const fetchTokens = async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setResults([]);
      return;
    }
    try {
      // This endpoint will be created later.
      const response = await fetch(`/api/v1/tokens/search?q=${searchQuery}`);
      if (!response.ok) {
        throw new Error('Failed to fetch tokens');
      }
      const data = await response.json();
      setResults(data);
      setIsDropdownVisible(true);
    } catch (error) {
      console.error("Failed to search for tokens:", error);
      setResults([]);
    }
  };

  const debouncedFetchTokens = useCallback(debounce(fetchTokens, 300), []);

  useEffect(() => {
    debouncedFetchTokens(query);
  }, [query, debouncedFetchTokens]);

  const handleSelectToken = (token: Token) => {
    setQuery(token.symbol);
    setTradeConfig({ tokenSymbol: token.symbol, tokenExchange: token.exchange });
    setIsDropdownVisible(false);
    setResults([]);
  };

  return (
    <div className="relative w-full">
      <label className="text-sm font-medium">Token</label>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value.toUpperCase())}
        onFocus={() => setIsDropdownVisible(true)}
        onBlur={() => setTimeout(() => setIsDropdownVisible(false), 150)} // Delay hiding to allow click
        className="h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        placeholder="Search for a token..."
      />
      {isDropdownVisible && results.length > 0 && (
        <div className="absolute z-10 mt-1 w-full rounded-md border bg-card text-card-foreground shadow-lg">
          <ul className="max-h-60 overflow-auto rounded-md p-1">
            {results.map((token) => (
              <li
                key={token.id}
                className="cursor-pointer rounded-sm p-2 text-sm hover:bg-accent"
                onClick={() => handleSelectToken(token)}
              >
                <div className="font-semibold">{token.symbol}</div>
                <div className="text-xs text-muted-foreground">{token.description}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
