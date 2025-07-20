
'use client';

import { useEffect, useState } from 'react';
import Header from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import NewClientForm from '@/components/clients/NewClientForm';
import toast from 'react-hot-toast';
import Link from 'next/link';

interface Client {
  id: string;
  name: string;
  client_id: string;
}

export default function ClientManagementPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showNewClientForm, setShowNewClientForm] = useState(false);

  const fetchClients = async () => {
    setLoading(true);
    setError(null);
    const promise = fetch('/api/v1/clients').then(async (response) => {
      if (!response.ok) {
        throw new Error(`Failed to fetch clients: ${response.statusText}`);
      }
      return response.json();
    });

    toast.promise(promise, {
      loading: 'Loading clients...',
      success: (data: Client[]) => {
        setClients(data);
        setLoading(false);
        return 'Clients loaded successfully!';
      },
      error: (err) => {
        console.error("Error fetching clients:", err);
        setError(err instanceof Error ? err.message : "An unknown error occurred");
        setLoading(false);
        return `Failed to load clients: ${err instanceof Error ? err.message : 'Unknown error'}`;
      },
    });
  };

  useEffect(() => {
    fetchClients();
  }, []);

  if (loading) {
    return <div className="p-6">Loading clients...</div>;
  }

  if (error) {
    return <div className="p-6 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Header title={''} />
      <main className="flex-1 p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Client Management</h1>
          <Button onClick={() => setShowNewClientForm(true)}>
            Add New Client
          </Button>
        </div>

        {showNewClientForm && (
          <NewClientForm
            onClose={() => setShowNewClientForm(false)}
            onClientAdded={fetchClients}
          />
        )}

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Existing Clients</h2>
          <div className="w-full overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-slate-50">
                <tr>
                  <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-foreground sm:pl-6">Client Name</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">Client ID</th>
                  <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border bg-card">
                {clients.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="text-center py-4 text-muted-foreground">
                      No clients added yet.
                    </td>
                  </tr>
                ) : (
                  clients.map((client) => (
                    <tr key={client.id} className="hover:bg-slate-50/50">
                      <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-foreground sm:pl-6">{client.name}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">{client.client_id}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">
                        <Link href={`/clients/${client.id}`} passHref>
                          <Button variant="outline" size="sm">
                            View Details
                          </Button>
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </main>
    </div>
  );
}
