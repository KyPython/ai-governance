# Parcel indexer workload contract

The synthetic parcel indexer receives object-created notifications through its queue. For each notification, the worker reads the referenced object from the `incoming/` prefix of the parcel-records bucket and updates an in-memory index.

The deployed workload requires:

- one object bucket that rejects public access;
- one encrypted queue with a 120-second visibility timeout;
- one worker execution role assumed only by the synthetic function service;
- permission for the worker to read objects delivered under the bucket's `incoming/` prefix.

The worker does not create, overwrite, delete, tag, or administer objects or buckets. Deployment administration is outside the worker execution role.
