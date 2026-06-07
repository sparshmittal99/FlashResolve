import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { TransactionService, Transaction } from './services/transaction';
import { interval, Subscription } from 'rxjs'; // 🚀 Added RxJS for the heartbeat

@Component({
  selector: 'app-root',
  standalone: true,
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent implements OnInit, OnDestroy {
  transactions = signal<Transaction[]>([]);
  
  // This variable holds our timer so we can stop it if the user leaves the page
  private pollingSub?: Subscription;

  constructor(private transactionService: TransactionService) {}

  ngOnInit() {
    // 1. Fetch data immediately when the page first loads
    this.fetchData();

    // 2. Start the heartbeat! Fetch new data every 3 seconds (3000ms)
    this.pollingSub = interval(3000).subscribe(() => {
      this.fetchData();
    });
  }

  fetchData() {
    this.transactionService.getAllTransactions().subscribe({
      next: (data: Transaction[]) => {
        // Because we are using Signals, .set() instantly redraws the HTML 
        // without us having to refresh the page!
        this.transactions.set(data);
      },
      error: (err: any) => {
        console.error('Failed to fetch from Java API', err);
      }
    });
  }

  // 3. Clean up the timer to prevent memory leaks if the app closes
  ngOnDestroy() {
    if (this.pollingSub) {
      this.pollingSub.unsubscribe();
    }
  }
}