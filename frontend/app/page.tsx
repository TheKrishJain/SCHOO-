import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8">School-OS</h1>
      <p className="mb-8 text-gray-600">The Operating System for Education</p>
      
      <div className="flex gap-4">
        <Link 
          href="/login" 
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
        >
          Login
        </Link>
      </div>
    </main>
  );
}