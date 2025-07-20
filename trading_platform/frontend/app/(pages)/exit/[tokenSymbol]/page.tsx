
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import toast from 'react-hot-toast';
import { Header } from '@/components/layout/Header';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface TokenHolder {
  client_id: string;
  client_name: string;
  quantity_held: number;
  avg_price: number;
}

export default function TokenExitPage() {
  const params = useParams();
  const tokenSymbol = params.tokenSymbol as string;

  const [tokenHolders, setTokenHolders] = useState<TokenHolder[]>([]);
  const [selectedClients, setSelectedClients] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Assuming a default exchange for now, or it could be passed via query param
  const tokenExchange = 'NSE'; 

  useEffect(() => {
    if (!tokenSymbol) return;

    const fetchTokenHolders = async () => {
      setLoading(true);
      setError(null);
      const promise = fetch(`/api/v1/tokens/${tokenSymbol}/holders?token_exchange=${tokenExchange}`).then(async (response) => {
        if (!response.ok) {
          throw new Error(`Failed to fetch token holders: ${response.statusText}`);
        }
        return response.json();
      });

      toast.promise(promise, {
        loading: 'Loading token holders...',
        success: (data: TokenHolder[]) => {
          setTokenHolders(data);
          setSelectedClients(data.map(holder => holder.client_id));
          setLoading(false);
          return 'Token holders loaded successfully!';
        },
        error: (err) => {
          console.error("Error fetching token holders:", err);
          setError(err instanceof Error ? err.message : "An unknown error occurred");
          setLoading(false);
          return `Failed to load token holders: ${err instanceof Error ? err.message : 'Unknown error'}`;
        },
      });
    };

    fetchTokenHolders();
  }, [tokenSymbol, tokenExchange]);

  const handleCheckboxChange = (clientId: string, isChecked: boolean) => {
    setSelectedClients((prevSelected) =>
      isChecked
        ? [...prevSelected, clientId]
        : prevSelected.filter((id) => id !== clientId)
    );
  };

  const handleExitAllSelected = async () => {
    if (selectedClients.length === 0) {
      toast.info('Please select at least one client to exit.');
      return;
    }

    const payload = {
      token_symbol: tokenSymbol,
      token_exchange: tokenExchange,
      clients_to_exit: selectedClients,
    };

    const promise = fetch('/api/v1/orders/exit-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(async (response) => {
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to execute bulk exit');
      }
      return response.json();
    });

    toast.promise(promise, {
      loading: 'Placing bulk exit orders...',
      success: (result) => {
        console.log('Bulk Exit Result:', result);
        // Optionally, re-fetch token holders to update the table
        // fetchTokenHolders(); 
        return 'Bulk exit orders placed successfully!';
      },
      error: (err) => {
        console.error("Error during bulk exit:", err);
        return `Bulk exit failed: ${err instanceof Error ? err.message : 'Unknown error'}`;
      },
    });
  };

  if (loading) {
    return <div className="p-6">Loading token holders...</div>;
  }

  if (error) {
    return <div className="p-6 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Header />
      <main className="flex-1 p-6">
        <h1 className="text-3xl font-bold mb-6">Exiting All Positions for {tokenSymbol.toUpperCase()}</h1>

        <Card className="p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Clients Holding {tokenSymbol.toUpperCase()}</h2>
          <div className="w-full overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-slate-50">
                <tr>
                  <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-foreground sm:pl-6">
                    Include
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">Client Name</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">Quantity Held</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">Avg Price</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border bg-card">
                {tokenHolders.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="text-center py-4 text-muted-foreground">
                      No clients currently holding {tokenSymbol.toUpperCase()}.
                    </td>
                  </tr>
                ) : (
                  tokenHolders.map((holder) => (
                    <tr key={holder.client_id} className="hover:bg-slate-50/50">
                      <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-foreground sm:pl-6">
                        <input
                          type="checkbox"
                          checked={selectedClients.includes(holder.client_id)}
                          onChange={(e) => handleCheckboxChange(holder.client_id, e.target.checked)}
                          className="h-4 w-4 text-primary focus:ring-primary border-border rounded"
                        />
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">{holder.client_name}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">{holder.quantity_held}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">${holder.avg_price.toFixed(2)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>

        <div className="mt-6 flex justify-end">
          <Button
            onClick={handleExitAllSelected}
            disabled={selectedClients.length === 0 || loading}
            className="bg-red-600 hover:bg-red-700 text-white"
          >
            Exit All Selected ({selectedClients.length})
          </Button>
        </div>
      </main>
    </div>
  );
}
