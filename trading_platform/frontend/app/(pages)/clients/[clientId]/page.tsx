
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import toast from 'react-hot-toast';
import Header from '@/components/layout/Header'; // Assuming Header component path
import { Card } from '@/components/ui/Card';     // Assuming Card component path
import ActiveTradesTable from '@/components/client/ActiveTradesTable';

interface ClientDetails {
  id: string;
  name: string;
  client_id: string;
  // Add other client details as needed
}

interface ActiveTrade {
  symbol: string;
  quantity: number;
  avg_price: number;
  ltp: number;
  // Add any other relevant trade properties
}

export default function ClientDetailPage() {
  const params = useParams();
  const clientId = params.clientId as string;

  const [client, setClient] = useState<ClientDetails | null>(null);
  const [activeTrades, setActiveTrades] = useState<ActiveTrade[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!clientId) return;

    const fetchClientData = async () => {
      setLoading(true);
      setError(null);
      
      const clientPromise = fetch(`/api/v1/clients/${clientId}`).then(async (res) => {
        if (!res.ok) {
          throw new Error(`Failed to fetch client details: ${res.statusText}`);
        }
        return res.json();
      });

      const tradesPromise = fetch(`/api/v1/clients/${clientId}/active-trades`).then(async (res) => {
        if (!res.ok) {
          throw new Error(`Failed to fetch active trades: ${res.statusText}`);
        }
        return res.json();
      });

      toast.promise(Promise.all([clientPromise, tradesPromise]), {
        loading: 'Loading client data...',
        success: ([clientData, tradesData]) => {
          setClient(clientData);
          setActiveTrades(tradesData);
          setLoading(false);
          return 'Client data loaded successfully!';
        },
        error: (err) => {
          console.error("Error fetching client data:", err);
          setError(err instanceof Error ? err.message : "An unknown error occurred");
          setLoading(false);
          return `Failed to load client data: ${err instanceof Error ? err.message : 'Unknown error'}`;
        },
      });
    };

    fetchClientData();
  }, [clientId]);

  if (loading) {
    return <div className="p-6">Loading client details...</div>;
  }

  if (error) {
    return <div className="p-6 text-red-500">Error: {error}</div>;
  }

  if (!client) {
    return <div className="p-6">Client not found.</div>;
  }

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Header title={''} />
      <main className="flex-1 p-6">
        <h1 className="text-3xl font-bold mb-6">Client: {client.name} ({client.client_id})</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-2">Portfolio Size</h3>
            <p className="text-2xl font-bold text-primary">$100,000.00</p> {/* Placeholder */}
          </Card>
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-2">Available Capital</h3>
            <p className="text-2xl font-bold text-primary">$25,000.00</p> {/* Placeholder */}
          </Card>
          {/* Add more key metrics cards as needed */}
        </div>

        <ActiveTradesTable activeTrades={activeTrades} clientId={client.client_id} />
      </main>
    </div>
  );
}
