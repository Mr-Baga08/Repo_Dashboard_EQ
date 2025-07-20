'use client';

import { useEffect } from 'react';
import { useDashboardStore } from '@/lib/store/useDashboardStore';

export default function ClientExecutionTable() {
  const { clients, quantities, fetchClients, setQuantity } = useDashboardStore();

  useEffect(() => {
    // Fetch clients when the component mounts
    fetchClients();
  }, [fetchClients]);

  return (
    <div className="w-full overflow-x-auto">
      <table className="min-w-full divide-y divide-border">
        <thead className="bg-slate-50">
          <tr>
            <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-foreground sm:pl-6">Client Name</th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">Client ID</th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">Available Funds</th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">Real-time P/L</th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">Quantity</th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">Margin</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border bg-card">
          {clients.map((client) => (
            <tr key={client.id} className="hover:bg-slate-50/50">
              <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-foreground sm:pl-6">{client.name}</td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">{client.client_id}</td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">$0.00</td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">$0.00</td>
              <td className="whitespace-nowrap px-3 py-4 text-sm">
                <input
                  type="number"
                  value={quantities[client.id] || ''}
                  onChange={(e) => setQuantity(client.id, parseInt(e.target.value, 10) || 0)}
                  className="h-9 w-24 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="0"
                />
              </td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">$0.00</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
