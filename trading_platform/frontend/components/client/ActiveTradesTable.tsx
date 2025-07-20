
import { useState, useEffect } from 'react';
import { useDashboardStore } from '@/lib/store/useDashboardStore';
import useRealtimePL from '@/lib/hooks/useRealtimePL';
import { Button } from '@/components/ui/Button'; // Assuming you have a Button component
import toast from 'react-hot-toast';

interface ActiveTrade {
  symbol: string;
  quantity: number;
  avg_price: number;
  ltp: number;
  // Add any other relevant trade properties
}

interface ActiveTradesTableProps {
  activeTrades: ActiveTrade[];
  clientId: string; // Pass clientId to filter real-time P/L
}

export default function ActiveTradesTable({ activeTrades, clientId }: ActiveTradesTableProps) {
  const { realtimePL, updatePL } = useDashboardStore();

  // Integrate the real-time P/L hook for this specific client
  useRealtimePL({
    onMessage: (data) => {
      // Only update if the message is for the current client
      if (data.clientId === clientId) {
        updatePL(data.clientId, data.pnl);
      }
    },
  });

  const handleExitTrade = async (trade: ActiveTrade) => {
    console.log(`Exiting trade for ${trade.symbol}`);
    // Implement actual trade exit logic here (e.g., API call)
    const exitPromise = new Promise(async (resolve, reject) => {
      try {
        // Placeholder for actual API call to exit a single trade
        // This would typically call an endpoint like /api/orders/exit-single-trade
        // For now, simulate success/failure
        const response = await fetch('/api/mock-exit-trade', { method: 'POST', body: JSON.stringify(trade) });
        if (!response.ok) {
          throw new Error('Failed to exit trade');
        }
        resolve(`Successfully exited ${trade.symbol}`);
      } catch (error) {
        reject(`Failed to exit ${trade.symbol}: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    });

    toast.promise(exitPromise, {
      loading: `Exiting ${trade.symbol}...`,
      success: (message) => message as string,
      error: (error) => error,
    });
  };

  return (
    <div className="w-full overflow-x-auto">
      <h2 className="text-xl font-semibold mb-4">Active Trades</h2>
      <table className="min-w-full divide-y divide-border">
        <thead className="bg-slate-50">
          <tr>
            <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-foreground sm:pl-6">Token</th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">Avg Price</th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">P/L</th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">Quantity</th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">Margin to Exit</th>
            <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border bg-card">
          {activeTrades.length === 0 ? (
            <tr>
              <td colSpan={6} className="text-center py-4 text-muted-foreground">
                No active trades found.
              </td>
            </tr>
          ) : (
            activeTrades.map((trade, index) => {
              // For simplicity, using the overall client P/L for each trade. 
              // In a real scenario, P/L would be per-trade or per-symbol.
              const pnlValue = realtimePL[clientId]; 
              const pnlColorClass = pnlValue !== undefined
                ? (pnlValue >= 0 ? 'text-green-500' : 'text-red-500')
                : 'text-muted-foreground';
              const formattedPnl = pnlValue !== undefined
                ? `${pnlValue.toFixed(2)}`
                : '---';

              return (
                <tr key={index} className="hover:bg-slate-50/50">
                  <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-foreground sm:pl-6">{trade.symbol}</td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">${trade.avg_price.toFixed(2)}</td>
                  <td className={`whitespace-nowrap px-3 py-4 text-sm ${pnlColorClass}`}>{formattedPnl}</td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">{trade.quantity}</td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">$0.00</td> {/* Placeholder */}
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">
                    <Button onClick={() => handleExitTrade(trade)} variant="outline" size="sm">
                      Exit
                    </Button>
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}
